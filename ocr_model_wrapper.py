"""
OCR 模型封装模块
用于加载和推理 MixTex 微调模型
"""
import os
import torch
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from transformers import (
    VisionEncoderDecoderModel,
    AutoTokenizer,
    AutoImageProcessor,
)
from peft import PeftModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRModelWrapper:
    """OCR 模型封装类"""
    
    def __init__(self, checkpoint_dir: str, base_model_path: str = None, device: str = None):
        """
        初始化模型
        
        Args:
            checkpoint_dir: 微调模型 checkpoint 目录路径
            base_model_path: 基础模型路径（如果是 LoRA checkpoint 则必须提供）
            device: 设备 ('cuda' 或 'cpu')，默认自动检测
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.device = torch.device(device)
        logger.info(f"使用设备: {self.device}")
        
        # 加载模型
        self.model, self.tokenizer, self.image_processor = self._load_model(
            checkpoint_dir, base_model_path
        )
        logger.info("模型加载完成")
    
    def _load_model(self, checkpoint_dir: str, base_model_path: str = None):
        """加载模型和处理器"""
        logger.info(f"从 {checkpoint_dir} 加载模型...")
        
        # 检查是否是 LoRA checkpoint
        adapter_config_path = os.path.join(checkpoint_dir, "adapter_config.json")
        
        if os.path.exists(adapter_config_path):
            if not base_model_path:
                # 尝试使用默认的基础模型路径
                base_model_path = "MixTex/ZhEn-Latex-OCR"
                logger.warning(f"检测到 LoRA checkpoint，使用默认基础模型: {base_model_path}")
            
            logger.info(f"检测到 LoRA checkpoint，从基础模型 {base_model_path} 加载...")
            model = VisionEncoderDecoderModel.from_pretrained(base_model_path)
            tokenizer = AutoTokenizer.from_pretrained(base_model_path)
            image_processor = AutoImageProcessor.from_pretrained(base_model_path)
            
            logger.info("将 LoRA 适配器加载到 decoder ...")
            decoder_with_lora = PeftModel.from_pretrained(model.decoder, checkpoint_dir)
            decoder_with_lora = decoder_with_lora.merge_and_unload()  # 合并权重便于推理
            model.decoder = decoder_with_lora
        else:
            # 全量模型
            logger.info("检测到全量模型 checkpoint")
            model = VisionEncoderDecoderModel.from_pretrained(checkpoint_dir)
            tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
            image_processor = AutoImageProcessor.from_pretrained(checkpoint_dir)
        
        model.to(self.device)
        model.eval()
        return model, tokenizer, image_processor
    
    def _preprocess_image(self, image: Image.Image, enhance: bool = True) -> Image.Image:
        """
        图片预处理：调整尺寸到训练数据范围、增强对比度、去噪等
        
        Args:
            image: 原始 PIL Image 对象
            enhance: 是否启用图片增强
        
        Returns:
            预处理后的图片
        """
        # 确保图片是 RGB 格式
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        original_size = image.size
        width, height = original_size
        logger.info(f"原始图片尺寸: {width}x{height}")
        
        # 保持原图宽高比，将图片缩放到几十到几百像素的量级
        # 目标范围：最小边至少50像素，最大边不超过500像素
        min_size = 30   # 最小边目标尺寸
        max_size = 600  # 最大边目标尺寸
        
        # 计算当前最大边和最小边
        max_dim = max(width, height)
        min_dim = min(width, height)
        
        # 计算缩放比例（保持宽高比）
        scale_ratio = 1.0
        
        # 如果图片太大（最大边超过max_size），缩小
        if max_dim > max_size:
            scale_ratio = max_size / max_dim
            logger.info(f"图片过大，缩小 {scale_ratio:.3f} 倍")
        # 如果图片太小（最小边小于min_size），放大
        elif min_dim < min_size:
            scale_ratio = min_size / min_dim
            logger.info(f"图片过小，放大 {scale_ratio:.3f} 倍")
        
        # 按比例调整尺寸（保持宽高比）
        if scale_ratio != 1.0:
            new_width = int(width * scale_ratio)
            new_height = int(height * scale_ratio)
            logger.info(f"图片尺寸调整: {original_size} -> ({new_width}, {new_height}), 宽高比保持不变: {new_width/new_height:.2f}")
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            logger.info(f"图片尺寸合适，无需调整")
        
        if not enhance:
            return image
        
        # 转换为灰度图进行质量检测
        gray = image.convert("L")
        
        # 计算图片的对比度和亮度统计
        img_array = np.array(gray)
        mean_brightness = np.mean(img_array)
        std_brightness = np.std(img_array)  # 标准差反映对比度
        
        # 如果图片对比度较低或亮度异常，进行增强
        if std_brightness < 30 or mean_brightness < 50 or mean_brightness > 200:
            logger.info(f"检测到图片质量较低 (亮度={mean_brightness:.1f}, 对比度={std_brightness:.1f})，进行增强处理")
            
            # 增强对比度
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # 增强20%对比度
            
            # 轻微增强锐度
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
        
        final_size = image.size
        logger.info(f"最终图片尺寸: {final_size[0]}x{final_size[1]}")
        
        return image
    
    def predict(self, image: Image.Image, max_length: int = 512, enhance: bool = True) -> str:
        """
        对图片进行 OCR 识别
        
        Args:
            image: PIL Image 对象
            max_length: 生成的最大长度（默认512，支持更长的公式）
            enhance: 是否启用图片增强预处理
        
        Returns:
            识别出的 LaTeX 代码字符串
        """
        # 预处理图片
        image = self._preprocess_image(image, enhance=enhance)
        
        # 使用 image_processor 进行模型特定的预处理
        pixel_values = self.image_processor(
            images=[image], 
            return_tensors="pt"
        ).pixel_values.to(self.device)
        
        # 模型推理
        with torch.no_grad():
            generated_ids = self.model.generate(
                pixel_values, 
                max_length=max_length,
                num_beams=5,  # 使用beam search提高质量
                early_stopping=True
            )
        
        # 解码
        latex_code = self.tokenizer.batch_decode(
            generated_ids, 
            skip_special_tokens=True
        )[0].strip()
        
        return latex_code





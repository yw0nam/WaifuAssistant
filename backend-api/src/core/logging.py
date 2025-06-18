import logging


def setup_logging(
    logger_name: str = "waifu_backend", level: int = logging.INFO
) -> logging.Logger:
    """로깅 설정"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # 핸들러가 이미 있으면 중복 방지
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

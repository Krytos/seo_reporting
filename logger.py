# Add this to main.py
# log = logger.setup_applevel_logger(file_name='debug.log')

import logging
import sys

import colorlog

APP_LOGGER_NAME = sys.path[0].split("\\")[-1]


def setup_applevel_logger(logger_name=APP_LOGGER_NAME, file_name=None):
	logger = colorlog.getLogger(logger_name)
	logger.setLevel(logging.DEBUG)
	file_formatter = logging.Formatter(
		fmt="%(asctime)s.%(msecs)03d - %(threadName)s - %(name)s: %(lineno)i - %(levelname)s - %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S"
	)
	secondary = {
		'message': {
			"INFO": "cyan"
		}, 'level': {
			"DEBUG": "blue", "INFO": "green", "WARNING": "yellow", "ERROR": "red", "CRITICAL": "red,bg_white"
		}

	}
	formatter = colorlog.ColoredFormatter(
		"%(asctime)s.%(msecs)03d - %(threadName)s - %(name)s: %(lineno)i%(level_log_color)s - "
		"%(levelname)s - %(reset)s%(message_log_color)s%(message)s", datefmt="%Y-%m-%d %H:%M:%S",
		secondary_log_colors=secondary, style="%"
	)
	# sh = logging.StreamHandler(sys.stdout)
	sh = colorlog.StreamHandler(sys.stdout)
	sh.setFormatter(formatter)
	logger.handlers.clear()
	logger.addHandler(sh)
	if file_name:
		with open(file_name, "w") as f:
			f.write("")
		fh = logging.FileHandler(sys.path[0] + "/" + file_name)
		fh.setFormatter(file_formatter)
		logger.addHandler(fh)
	return logger


def get_logger(module_name):
	return colorlog.getLogger(APP_LOGGER_NAME).getChild(module_name)

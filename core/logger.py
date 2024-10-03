import logging.config

# matplotlib_logger = logging.getLogger('matplotlib')
# matplotlib_logger.setLevel(logging.ERROR)

def setup_logger(logger_name=__name__):
	logger = logging.getLogger(logger_name)
	return logger

def print_active_loggers():
    for name, logger in logging.root.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            print(f"Logger: {name}, Level: {logging.getLevelName(logger.level)}")

def set_third_party_loggers_level(level='ERROR', exceptions=['core.logger',__name__], exception_level='DEBUG'):
    for name, logger in logging.root.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            if name in exceptions:
                logging.getLogger(name).setLevel(getattr(logging, exception_level))
            else:
                logging.getLogger(name).setLevel(getattr(logging, level))

def set_logger_config(level='DEBUG',third_party=False):
	logging_config = {
		'version': 1,
		'disable_existing_loggers': third_party, # False allows third party logs
		# 'filters': {},
		'formatters': {
			'basic': {
				'format': "{asctime} - {levelname} - {filename}: {message}",
				'style': "{",
				'datefmt': "%H:%M:%S",
			}
		},
		'handlers': {
			'stdout': {
				'class':'logging.StreamHandler', 
				'formatter': 'basic',
				'stream' : 'ext://sys.stdout', # external ???
			}
		},
		'loggers': {
			'root': {
				'level': level,
				'handlers': ['stdout'],
			}
		},
	}

	logging.config.dictConfig(config=logging_config)

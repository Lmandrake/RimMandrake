glob.glob and an os.path.lexists/exists guard both turn an unreadable directory into 'empty'. A safety reader (helpers alive?) must call os.listdir directly: FileNotFoundError = none, any other OSError = UNMEASURED/hold (GPT review2-4).
home: NONE

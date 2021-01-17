import json
class GlobalSettings:
    settings = {}
    proxies = {
        'http' : '',
        'https' : ''
    }
    inited = False
    download_thumb = False
    
    def __init__(self):
        if not GlobalSettings.inited:
            file = open("Settings.txt", 'rt')
            lines = file.readlines()
            text = ''
            for line in lines:
                if (line.endswith('\n')):                    
                    line = line.rstrip()
                text += line
            GlobalSettings.settings = json.loads(text)
            GlobalSettings.proxies['http'] = GlobalSettings.settings['proxies']
            GlobalSettings.proxies['https'] = GlobalSettings.settings['proxies']
            GlobalSettings.download_thumb = GlobalSettings.settings['download_thumb']
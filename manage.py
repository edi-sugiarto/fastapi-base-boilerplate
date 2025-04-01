import textwrap

import uvicorn
from colorama import Fore, init

from config.config import settings

init(autoreset=True)  # Initializes Colorama

if __name__ == "__main__":
    version = settings.APP_VERSION
    print(
        textwrap.dedent(
            rf"""{Fore.BLUE}
     _     __ _             ____ _                                   
    / \   / _| |_ ___ _ __ / ___| | __ _ ___ ___                     
   / _ \ | |_| __/ _ \ '__| |   | |/ _` / __/ __|                    
  / ___ \|  _| ||  __/ |  | |___| | (_| \__ \__ \                    
 /_/   \_\_|  \__\___|_|   \____|_|\__,_|___/___/                    
  _____         _      _    ____ ___           ____                  
 |  ___|_ _ ___| |_   / \  |  _ \_ _|         | __ )  __ _ ___  ___  
 | |_ / _` / __| __| / _ \ | |_) | |   _____  |  _ \ / _` / __|/ _ \ 
 |  _| (_| \__ \ |_ / ___ \|  __/| |  |_____| | |_) | (_| \__ \  __/ 
 |_|  \__,_|___/\__/_/   \_\_|  |___|         |____/ \__,_|___/\___| 
                                                                                                       
 version: {version}
    """
        )
    )

    uvicorn.run(
        "app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True
    )

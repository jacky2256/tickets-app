from app.wdm import SBDriver

if __name__ == "__main__":
    sbdriver = SBDriver()
    sbdriver.fetch_content('https://whatismyipaddress.com/')
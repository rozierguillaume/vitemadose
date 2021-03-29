from time import sleep
from selenium import webdriver

story = 'https://medium.com/dropout-analytics/selenium-and-geckodriver-on-mac-b411dbfe61bc'
story = story + '?source=friends_link&sk=18e2c2f07fbe1f8ae53fef5ad57dbb12'   # 'https://bit.ly/2WaKraO' <- short link

def gecko_test(site_000=story):
    """
    simple overview:
        1) set up webdriver
        2) load this article 
        3) close up shop 
    
    input:
        >> site_000
            > default: url of this article ('friend link')
    """
    # set the driver 
    driver = webdriver.Firefox()

    # load this article 
    driver.get(site_000)
    # and chill a bit
    sleep(7)

    # k, cool. let's bounce. 
    driver.quit()


# make runable 
if __name__ == '__main__':
    # here we go
    gecko_test()

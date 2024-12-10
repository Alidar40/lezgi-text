import os
from urllib.request import urlopen
import requests
from pathlib import Path
import time

from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, Firefox, Edge, Safari, Ie
from selenium.common import ElementNotInteractableException, NoSuchDriverException


def scrap_lezgi_gazet(output_dir: str | os.PathLike = "./lezgi_gazet_pdf") -> None:
    archive_url = "https://lezgigazet.ru/archives/project/page/0"

    output_dir = "./lezgi_gazet_pdf" if output_dir is None else output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    pbar = tqdm(desc="Page")
    next_page_url = archive_url
    while next_page_url:
        page = urlopen(next_page_url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        
        page_entries = soup.find_all('h3', {"class": "cmsmasters_archive_item_title entry-title"})
        for entry_title in tqdm(page_entries, desc="Documents on page", leave=False):
            entry_url = entry_title.find('a').get('href')
            
            download_page = urlopen(entry_url)
            download_html = download_page.read().decode("utf-8")
            download_soup = BeautifulSoup(download_html, "html.parser")
        
            pdf_url = download_soup.find('article').find('a').get('href')
            pdf_file_name = '_'.join(pdf_url.split('/')[-3:])
            output_file = output_dir / pdf_file_name
            if output_file.exists():
                continue

            response = requests.get(pdf_url)

            with open(output_file, 'wb') as f:
                f.write(response.content)

        next_page_element = soup.find('a', {"class": "next page-numbers"})
        if next_page_element:
            next_page_url = next_page_element.get('href')
        else:
            next_page_url = None
        pbar.update(1)
    pbar.close()


def scrap_tsiyi_dunya(output_dir: str | os.PathLike = "./tsiyi_dunya_pdf") -> None:
    base_url = "https://akhtymr.ru/"
    archive_url = f"{base_url}/site/section?id=202"

    output_dir = "./tsiyi_dunya_pdf" if output_dir is None else output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    driver = None
    for browser_driver in [Chrome, Firefox, Edge, Safari, Ie]:
        try:
            driver = browser_driver()
        except NoSuchDriverException:
            continue
        break

    if driver is None:
        raise RuntimeError("No supported browsers installed!")

    driver.get(archive_url)

    time.sleep(3)
    # close_dialog_button = driver.find_element(by="css selector", value='.js__minrates-dialog-close')
    # close_dialog_button.click()

    agreement_acceptance_button = driver.find_element(by="id", value="agreement-acceptance-button")
    agreement_acceptance_button.click()

    # avoiding ElementClickInterceptedException: 
    # Message: Element <button class="show-more" type="button">
    # is not clickable because another element <p> obscures it
    time.sleep(3)

    done_iterating = False
    while not done_iterating:
        show_more_button = driver.find_element(by="css selector", value='.show-more')
        try:
            show_more_button.click()
            time.sleep(1)
        except ElementNotInteractableException:
            done_iterating = True

    soup = BeautifulSoup(driver.page_source, 'lxml')

    driver.quit()

    for vp_pub_list_item in tqdm(soup.find_all("a", {"class": "vp-pub-list-item"}), desc="Documents"):
        item_url = base_url + vp_pub_list_item.get("href")

        item_page = urlopen(item_url)
        item_html = item_page.read().decode("utf-8")
        item_soup = BeautifulSoup(item_html, "html.parser")

        # There are pages without links to a pdf
        file_caption_element = item_soup.find("p", {"class": "file-caption"})
        if file_caption_element:
            pdf_url = base_url + file_caption_element.find("a").get("href")
            pdf_name = item_soup.find('title').get_text() + ".pdf"
        
            response = requests.get(pdf_url)
            with open(output_dir / pdf_name, 'wb') as f:
                f.write(response.content)


def scrap_erenlardin_ses(output_dir: str | os.PathLike = "./erenlardin_ses_pdf") -> None:
    base_url = "https://erenlar.ru/"
    archive_url = f"{base_url}/rajonnaya-gazeta-golos-erenlara/"

    output_dir = "./erenlardin_ses_pdf" if output_dir is None else output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # no pagination for this website as of end of 2024
    page = urlopen(archive_url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    for entry_title in tqdm(soup.find_all('td', {"class": "left top"}), desc="Documents"):
        a = entry_title.find('a')
        if not a:
            continue
        entry_url = a.get('href')

        pdf_url = base_url + entry_url


        output_file = output_dir / '_'.join(entry_url.split('/')[2:])
        if output_file.exists():
            continue

        response = requests.get(pdf_url)
        with open(output_file, 'wb') as f:
            f.write(response.content)


def scrap_dagdin_bulah(output_dir: str | os.PathLike = "./dagdin_bulah_pdf") -> None:
    base_url = "https://mrkurahskiy.ru/"
    archive_url = f"{base_url}press-tsentr/gazeta-gornyy-rodnik-"

    output_dir = "./dagdin_bulah_pdf" if output_dir is None else output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # no pagination for this website as fo end of 2024
    page = urlopen(archive_url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    for entry_title in tqdm(soup.find_all('a', {"class": "file"}), desc="Documents"):
        pdf_url = entry_title.get('href')

        if pdf_url.startswith('/file/download/'):
            pdf_url = base_url + pdf_url

        output_file = output_dir / pdf_url.split('/')[-1]
        if output_file.exists():
            continue

        response = requests.get(pdf_url)
        with open(output_file, 'wb') as f:
            f.write(response.content)


def scrap_samurdin_ses(output_dir: str | os.PathLike = "./samurdin_ses_pdf") -> None:
    base_url = "https://adminmr.ru/"
    archive_url = f"{base_url}Район/СМИ_«Самурдин_Сес»"

    output_dir = "./samurdin_ses_pdf" if output_dir is None else output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # no pagination for this website as fo end of 2024
    html = requests.get(archive_url).content
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find('div', {"class": "doc"})
    container = container.find('ul')

    for entry_title in tqdm(container.find_all('a'), desc="Documents"):
        pdf_url = base_url + entry_title.get('href')

        output_file = output_dir / pdf_url.split('/')[-1]
        if output_file.exists():
            continue

        response = requests.get(pdf_url)
        with open(output_file, 'wb') as f:
            f.write(response.content)


def scrap_cure_habar(output_dir: str | os.PathLike = "./cure_habar_pdf") -> None:
    base_url = "https://cure-online.ru/"
    archive_url = f"{base_url}/inova_block_issueset/41/card/"

    output_dir = "./cure_habar_pdf" if output_dir is None else output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    pbar = tqdm(desc="Page")
    next_page_url = archive_url
    while next_page_url:
        page = urlopen(next_page_url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        
        page_entries = soup.find_all('h2', {"class": "uil-mo-media-item-list-3__title"})
        for entry_title in tqdm(page_entries, desc="Documents on page", leave=False):
            entry_url = entry_title.find('a').get('href')
            entry_url = base_url + entry_url
            
            download_page = urlopen(entry_url)
            download_html = download_page.read().decode("utf-8")
            download_soup = BeautifulSoup(download_html, "html.parser")
        
            pdf_url = download_soup.find('div', {"class": "uil-form-controls-v2__control"}).find('a').get('href')
            pdf_url = base_url + pdf_url

            output_file = output_dir / '_'.join(pdf_url.split('/')[2:])
            if output_file.exists():
                continue

            response = requests.get(pdf_url)

            with open(output_file, 'wb') as f:
                f.write(response.content)

        next_page_element = soup.find('span', {"class": "uil-mo-paginator__next"})
        if next_page_element:
            next_page_url = base_url + next_page_element.find('a').get('href')
        else:
            next_page_url = None
        pbar.update(1)
    pbar.close()


def scrap_samur(output_dir: str | os.PathLike = "./samur_pdf") -> None:
    base_url = "https://samuronline.com/"
    archive_url = f"{base_url}archive"

    output_dir = "./samur_pdf" if output_dir is None else output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    pbar = tqdm(desc="Page")
    next_page_url = archive_url
    while next_page_url:
        page = urlopen(next_page_url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        
        for entry_title in tqdm(soup.find_all('div', {"class": ["col-lg-3", "col-6"]})):
            entry_url = entry_title.find('a').get('href')
            pdf_url = base_url + entry_url
            pdf_name = pdf_url.split('/')[-1]

            output_file = output_dir / pdf_name
            if output_file.exists():
                continue

            response = requests.get(pdf_url)

            # not found, 404 error
            if response.content.startswith(b"<!DOCTYPE html>"):
                continue

            with open(output_file, 'wb') as f:
                f.write(response.content)

        next_page_element = soup.find('a', {"class": "page-link", "aria-label": "Next"})
        if next_page_element:
            next_page_url = archive_url + next_page_element.get('href')
        else:
            next_page_url = None
        pbar.update(1)
    pbar.close()


def scrap_lit_dag(output_dir: str | os.PathLike = "./lit_dag_pdf") -> None:
    raise NotImplementedError()


def scrap_alam(output_dir: str | os.PathLike = "./alam_pdf") -> None:
    raise NotImplementedError()
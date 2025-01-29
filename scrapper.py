import os
import time
from datetime import datetime
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver(download_folder):
    print("Setting up the driver.")
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('prefs', {
        "download.default_directory": download_folder, 
        "download.prompt_for_download": False, 
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def navigate_to_procedimientos(driver):
    print("Navigating to procedimientos.")
    url = 'https://compranet.hacienda.gob.mx/web/login.html'
    driver.get(url)
    time.sleep(5)
    procedimientos = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[2]/div[1]/div[3]/a/div[2]/h5")
    procedimientos.click()
    time.sleep(12)

    all_handles = driver.window_handles
    driver.switch_to.window(all_handles[1])
    time.sleep(3)

def select_tipo_procedimiento(driver):
    print("Selecting tipo de procedimiento.")
    anuncios_vigentes = driver.find_element(By.XPATH, '//*[@id="p-tabpanel-0-label"]/span[1]')
    anuncios_vigentes.click()
    time.sleep(3)
    
    tipo_procedimiento_menu = driver.find_element(By.XPATH, '/html/body/app-root/app-sitiopublico/div/div[1]/div/app-menu/app-sitiopublico-filtro/div/form/div/div[7]/p-dropdown/div/div[2]/span')
    tipo_procedimiento_menu.click()

    wait = WebDriverWait(driver, 30)
    option = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-sitiopublico/div/div[1]/div/app-menu/app-sitiopublico-filtro/div/form/div/div[7]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[3]/li/span[1]")))
    option.click()
    time.sleep(2)

def apply_filters_and_search(driver, search_term):
    print("Applying filters and searching.")
    filtros_button = driver.find_element(By.XPATH, '/html/body/app-root/app-sitiopublico/div/div[1]/div/app-menu/app-sitiopublico-filtro/div/form/div/div[10]/p-button[1]/button/span[2]')
    filtros_button.click()
    time.sleep(6)

    nombre_search = driver.find_element(By.XPATH, '/html/body/app-root/app-sitiopublico/div/div[1]/div/app-menu/app-sitiopublico-filtro/div/form/div/div[20]/input')
    nombre_search.send_keys(search_term)

    wait = WebDriverWait(driver, 30)
    buscar_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-sitiopublico/div/div[1]/div/app-menu/app-sitiopublico-filtro/div/form/div/div[10]/p-button[3]/button/span[2]')))
    buscar_button.click()
    time.sleep(15)

def download_and_move_documents(driver, parent_element, src_folder, dst_folder):
    print("Downloading documents and moving them to the destination folder.")
    
    # Ensure destination folder exists
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
        print(f"Created folder: {dst_folder}")

    time.sleep(8)
    download_documents_list = parent_element.find_elements(By.CLASS_NAME, 'pi.pi-download')

    for doc in download_documents_list:
        # Scroll the document into view and click
        #driver.execute_script("arguments[0].scrollIntoView(true);", doc)
        time.sleep(5)

        # Click the download button
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(doc)).click()
            print("Document clicked for download.")
        except Exception as e:
            print(f"Error clicking the document: {e}")

        # Wait for the download to complete and then move the file
        wait_for_download_complete_and_move_file(src_folder, dst_folder)


def wait_for_download_complete_and_move_file(src_folder, dst_folder, timeout=10):
    print("Waiting for download to complete and moving file.")
    start_time = time.time()
    while True:
        # Check if the timeout has been reached
        if time.time() - start_time > timeout:
            print("Timeout waiting for download to complete.")
            break

        # List all files in the source folder
        files = os.listdir(src_folder)
        
        # Filter out incomplete files (like .crdownload in Chrome)
        completed_files = [f for f in files if (f.endswith('.pdf') or f.endswith('.docx') or f.endswith('.xlsx') or f.endswith('.csv')) and not f.endswith('.crdownload') and not f.endswith('.part')]

        # If there are completed files, move the latest one
        if completed_files:
            # Find the latest file based on creation time
            latest_file = max([os.path.join(src_folder, f) for f in completed_files], key=os.path.getctime)
            
            # Check if the file is old enough to be considered completely written
            if time.time() - os.path.getctime(latest_file) > 2:  # This delay is adjustable
                # Construct the destination file path
                dst_file = os.path.join(dst_folder, os.path.basename(latest_file))
                
                # Move the file
                os.rename(latest_file, dst_file)
                print(f"Moved {os.path.basename(latest_file)} to {dst_folder}")
                
                # Break after moving the file
                break

        # Wait for a short period before checking again
        time.sleep(1)

def extract_data(driver, parent_element_selector):
    print("Extracting data from the element.")
    try:
        # Get the current URL
        current_url = driver.current_url

        # Wait for the element to be present
        parent_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, parent_element_selector))
        )

        # Find all elements with class 'p-text-bold'
        bold_elements = parent_element.find_elements(By.CLASS_NAME, 'p-text-bold')

        data_dict = {"Source URL": current_url}
        for elem in bold_elements:
            key = elem.text.strip()
            br_sibling = driver.execute_script("return arguments[0].nextElementSibling;", elem)
            value_sibling = driver.execute_script("return arguments[0].nextElementSibling;", br_sibling)
            value = value_sibling.text.strip() if value_sibling else ""
            data_dict[key] = value

        return data_dict

    except Exception as e:
        print(f"Error in extract_data: {e}")
        return {}


def save_dict_to_csv(data_dict, filename):
    print(f"Saving data to CSV file: {filename}")
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Concepto', 'Valor']) 
        for key, value in data_dict.items():
            writer.writerow([key, value])

def main(search_term):
    print("Starting the main process.")
    download_folder_base = "/home/project/raw_data"
    current_date = datetime.now().strftime("%Y_%m_%d")

    driver = setup_driver(download_folder_base)
    navigate_to_procedimientos(driver)
    select_tipo_procedimiento(driver)
    apply_filters_and_search(driver, search_term)

    table_elements_count = len(driver.find_elements(By.CLASS_NAME, "p-link2"))
    
    for index in range(table_elements_count):
        print(f"Processing element {index + 1}")

        table_elements = driver.find_elements(By.CLASS_NAME, "p-link2")
        if index >= len(table_elements):
            print("No more elements to process.")
            break

        element = table_elements[index]
        element.click()
        time.sleep(14)

        # Selector for extracting data
        parent_element_number_data = 4 + index * 10
        parent_element_selector_data = f'//*[@id="p-tabpanel-{parent_element_number_data}"]/div/app-sitiopublico-detalle-datos-general-pc'
        data_dict = extract_data(driver, parent_element_selector_data)
        csv_filename = os.path.join(download_folder_base, f'{current_date}__{index + 1:02d}.csv')
        save_dict_to_csv(data_dict, csv_filename)

        # Selector for downloading and moving documents
        parent_element_number_download = 6 + index * 10
        parent_element_selector_download = f'//*[@id="p-tabpanel-{parent_element_number_download}"]/app-sitiopublico-detalle-anexos/div/div/p-table/div/div/div/div[2]'
        parent_element_download = driver.find_element(By.XPATH, parent_element_selector_download)
        download_and_move_documents(driver, parent_element_download, download_folder_base, f'../raw_data/{search_term}_{current_date}__{index + 1:02d}')

        time.sleep(5)
        driver.back()
        time.sleep(10)

    driver.quit()

if __name__ == "__main__":
    search_terms = ["limpieza"]

    for term in search_terms:
        try:
            print(f"Starting search for: {term}")
            main(term)
            print(f"Finished search for: {term}\n")
        except Exception as e:
            print(f"An error occurred during the search for '{term}': {e}")
            print("Continuing with next search term.\n")

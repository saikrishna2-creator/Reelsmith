from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:5173/upload")

    # Wait for the input elements to be ready
    page.wait_for_selector('input[id="video-file"]')

    # Set the input files
    page.locator('input[id="video-file"]').set_input_files('test_video.mp4')
    page.locator('input[id="music-file"]').set_input_files('test_music.mp3')

    page.screenshot(path="jules-scratch/verification/verification.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

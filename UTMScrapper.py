from bs4 import BeautifulSoup

# https://student.utm.utoronto.ca/examschedule/finalexams.php
class Scrapper:
    @staticmethod
    def scrape():
        html = "https://student.utm.utoronto.ca/examschedule/finalexams.php"
        exams = parse_exam_html(html)
        
    def parse_exam_html(html):
        '''
        Create a JSON object from the HTML page
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        soup.find()
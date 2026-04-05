import requests
import re
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def fetch_schedule(group_id=None, staff_id=None, week=None):
    if staff_id:
        url = f"https://ssau.ru/rasp?staffId={staff_id}"
    else:
        url = f"https://ssau.ru/rasp?groupId={group_id}"
    if week:
        url += f"&selectedWeek={week}"

    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    day_headers = []
    for head in soup.select('.schedule__head:not(:first-child)'):
        weekday = head.select_one('.schedule__head-weekday')
        date = head.select_one('.schedule__head-date')
        if weekday:
            day_headers.append({
                'weekday': weekday.text.strip(),
                'date': date.text.strip() if date else ''
            })

    day_count = len(day_headers)
    schedule_items_el = soup.select_one('.schedule__items')
    items = [el for el in schedule_items_el.children if el.name] if schedule_items_el else []

    rows = []
    idx = 0
    while idx < len(items):
        el = items[idx]
        if 'schedule__time' not in el.get('class', []):
            idx += 1
            continue

        times = [t.text.strip() for t in el.select('.schedule__time-item')]
        time_str = ' – '.join(times) if len(times) == 2 else (times[0] if times else '')
        idx += 1

        day_cells = []
        for _ in range(day_count):
            if idx < len(items) and 'schedule__item' in items[idx].get('class', []):
                cell_lessons = []
                for lb in items[idx].select('.schedule__lesson'):
                    lesson = {}
                    tc = lb.find('div', class_='schedule__lesson-type-chip')
                    if tc:
                        lesson['type'] = tc.text.strip()
                    d = lb.find('div', class_='schedule__discipline')
                    if d:
                        lesson['discipline'] = d.text.strip()
                    p = lb.find('div', class_='schedule__place')
                    if p:
                        lesson['place'] = p.text.strip()
                    t = lb.find('div', class_='schedule__teacher')
                    if t:
                        lesson['teacher'] = ' '.join(t.text.strip().split())
                        tl = t.find('a')
                        lesson['teacher_href'] = tl['href'] if tl else ''
                    gc = lb.find('div', class_='schedule__groups')
                    if gc:
                        gs = gc.find_all('a', class_='schedule__group')
                        lesson['groups'] = [{'name': g.text.strip(), 'href': g['href']} for g in gs]
                        sp = gc.find('span', class_='caption-text')
                        lesson['subgroup'] = sp.text.strip() if sp else ''
                    tcol = lb.find(class_=lambda c: c and 'lesson-type-' in c and '__color' in c)
                    if tcol:
                        for cls in tcol['class']:
                            if 'lesson-type-' in cls and '__color' in cls:
                                lesson['type_class'] = cls.replace('__color', '')
                                break
                    cell_lessons.append(lesson)
                day_cells.append(cell_lessons)
                idx += 1
            else:
                day_cells.append([])
        rows.append({'time': time_str, 'days': day_cells})

    def extract_week_num(el):
        if not el:
            return None
        m = re.search(r'selectedWeek=(\d+)', el.get('href', ''))
        return int(m.group(1)) if m else None

    return {
        'week': (soup.select_one('.week-nav-current_week') or soup.new_tag('x')).get_text(strip=True),
        'week_date': (soup.select_one('.week-nav-current_date') or soup.new_tag('x')).get_text(strip=True),
        'week_prev': extract_week_num(soup.select_one('.week-nav-prev')),
        'week_next': extract_week_num(soup.select_one('.week-nav-next')),
        'title': (soup.select_one('.info-block__title') or soup.new_tag('x')).get_text(strip=True),
        'description': (soup.select_one('.info-block__description') or soup.new_tag('x')).get_text(' | ', strip=True),
        'days': day_headers,
        'rows': rows,
    }

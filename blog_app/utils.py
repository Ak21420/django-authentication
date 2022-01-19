from datetime import datetime, timedelta, date
from calendar import HTMLCalendar
from .models import Post


class Calendar(HTMLCalendar):
    def __init__(self, date, year, month):
        self.date = date
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, posts):
        posts_per_day = posts.filter(date_posted__day=day)
        d = ''
        for event in posts_per_day:
            d += f'<li> {event.title} </li>'

        if day != 0:
            print(date.today())
            if d:
                return f"<td style='background-color:pink'><span class='date'>{day}</span><ul> {d} </ul></td>"
            elif date.today().day == day:
                return f"<td  style='background-color:skyblue'><span class='date'>{day}</span><ul> {d} </ul></td>"
            else:
                return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, posts):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, posts)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        # posts = Post.objects.filter(date_posted=self.date)
        posts = Post.objects.filter(date_posted__year=self.year, date_posted__month=self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, posts)}\n'
        return cal

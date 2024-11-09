from bs4 import BeautifulSoup

with open("ToScrape1.html", "r") as html_file:
    content = html_file.read() #reads through whole file

    soup = BeautifulSoup(content,"html.parser")
    #Gives us access to the html parser for the content
    # print(soup.prettify())

    # tags = soup.find("h5")
    #Searches for the first element of the h5 tag
    #print(tags)
    # courses_html_tags = soup.find_all("h5")
    #Now contains all lines with h5 tag
    # print(courses_html_tags)

    # for course in courses_html_tags:
    #     print(course.text) #Prints the text of the course lines

    course_cards = soup.find_all("div", class_="card")
    #Class must be underscored!

    for course in course_cards:
        # print(course.h5)
        course_name = course.h5.text
        # print(course_name)
        course_price = course.a.text.split()[-1]
        #The split() splits the string based on a space
        #The [-1] returns the last element of the split array.
        # print(course_price)
        print(f"{course_name} costs {course_price}")

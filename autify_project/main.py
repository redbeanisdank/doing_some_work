import requests

from argparse import ArgumentParser
from os import getcwd

from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, DateTime, func, desc
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///url.db', echo=True)

Base = declarative_base()


class URL(Base):
    __tablename__ = "urls"
    id = Column('id', Integer, primary_key=True)
    link = Column('link', String)


class URLMetadata(Base):
    __tablename__ = "url_metadata"
    id = Column('id', Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey("urls.id"))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    links = Column(Integer)
    images = Column(Integer)


Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


def get_url_data(requested_url):
    """
    Given a url will attempt to obtain the contents and title. by using the requests library we can leverage
    and gurantee we receive a well formed url to work with.
    :param requested_url: assumption a well formatted string of the form http://www.fake.com
    :return: title, contents
    """
    title = None
    contents = None
    try:
        req = requests.get(requested_url)
        contents = req.content
        title = requested_url.split("//")[-1]
    except Exception as e:
        print(f"there was a problem downloading requested url: {e}")
    return title, contents


def download_url_contents(url_title, url_contents):
    """
    Writes the contents of the given url's to the cwd.
    :param url_title:
    :param url_contents:
    :return:
    """
    try:
        with open(f"{getcwd()}/{url_title}.html", "w") as html_file:
            decoded_contents = url_contents.decode()
            html_file.write(decoded_contents)
    except Exception as e:
        print(f"there was a problem downloading the file:{e}")


def fetch(urls):
    """
    the fetch function simulates in a simple manner albiet bare bones functionality. allows multiple urls.
    :param urls:
    :return:
    """
    for url in urls:
        try:
            title, contents = get_url_data(url)
            download_url_contents(title, contents)
            soup = BeautifulSoup(contents, "html.parser")
            links = soup.find("a", href=True)
            images = soup.find("img")
            links_len = len(links) if links else 0
            images_count = len(images) if images else 0
            url = URL(link=title)
            url_metadata = URLMetadata(id=url.id, links=links_len, images=images_count)
            #TODO didnt finish. missing case where more metadata is added for an already created/queryed link ran out of time

            session.add(url)
            session.add(url_metadata)
            session.commit()
            session.close()


        except Exception as e:
            print(f"error fetching url: {url} due to exception: {e}.")
            raise e


def get_metadata(urls):
    for url in urls:
        last_url_metadata = session.query(URLMetadata).order_by(desc('time_created')).first()
        if last_url_metadata:
            formatted_url = url.split("//")[-1]
            print(f"""
            site: {formatted_url}\n
            num_links: {last_url_metadata.links}\n
            images: {last_url_metadata.images}\n
            last_fetch: {last_url_metadata.time_created}\n
            """
                  )


if __name__ == '__main__':  # pragma: no cover

    parser = ArgumentParser(
        prog="fetch",
        description="fetch the contents of the urls supplied as command line arguments"
    )
    parser.add_argument("urls", nargs="+", type=str)
    metadata = parser.add_argument_group("query metadata of the supplied urls")
    metadata.add_argument("-m", "--metadata", action="store_true")
    args = parser.parse_args()
    if args.metadata:
        get_metadata(args.urls)
    else:
        fetch(args.urls)

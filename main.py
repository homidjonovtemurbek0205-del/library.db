from sqlalchemy import create_engine, ForeignKey, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

engine = create_engine("sqlite:///library.db", echo=False)

class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str]
    birth_year: Mapped[int]
    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    price: Mapped[float]
    published_year: Mapped[int]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")

Base.metadata.create_all(bind=engine)

with Session(engine) as session:
        a1 = Author(full_name="Guido van Rossum", birth_year=1956)
        a2 = Author(full_name="Robert Martin", birth_year=1952)
        a3 = Author(full_name="Martin Fowler", birth_year=1963)
        a4 = Author(full_name="Mark Lutz", birth_year=1965)
        a5 = Author(full_name="Abdulla Qodiriy", birth_year=1894)
        
        k1 = Book(title="Python Core", price=85000, published_year=2010), Book(title="Advanced Python", price=120000, published_year=2018)
        k2 = Book(title="Clean Code", price=150000, published_year=2008), Book(title="Clean Architecture", price=165000, published_year=2017)
        k3 = Book(title="Refactoring", price=140000, published_year=2018), Book(title="Enterprise Patterns", price=180000, published_year=2002)
        k4 = Book(title="Learning Python", price=210000, published_year=2013), Book(title="Programming Python", price=250000, published_year=2020)
        k5 = Book(title="O'tkan kunlar", price=50000, published_year=1925), Book(title="Mehrobdan chayon", price=45000, published_year=1928)
        
        session.add_all([a1, a2, a3, a4, a5])
        session.commit()

with Session(engine) as session:
    # Barcha authorlarni chiqaring
    for a in session.execute(select(Author)).scalars():
        print(a.full_name)

    # Barcha booklarni chiqaring
    for b in session.execute(select(Book)).scalars():
        print(b.title)

    # Har bir author va uning booklarini chiqaring
    for a in session.execute(select(Author)).scalars():
        print(f"\n{a.full_name}:")
        for b in a.books:
            print(f"  -> {b.title}")

    # Faqat ma’lum bir authorning booklarini chiqaring
    author = session.execute(
        select(Author).where(Author.full_name == "Robert Martin")
    ).scalars().first()

    if author:
        print(f"{author.full_name} ning kitoblari:")
        
    # Narxi 100000 dan katta bo‘lgan booklarni chiqaring
    for b in session.execute(select(Book).where(Book.price > 100000)).scalars():
        print(f"{b.title} - {b.price}")

    # 2015-yildan keyin chiqqan booklarni chiqaring
    for b in session.execute(select(Book).where(Book.published_year > 2015)).scalars():
        print(f"{b.title} ({b.published_year})")

    # Eng qimmat bookni chiqaring
    qimmat_kitob = session.execute(select(Book).order_by(Book.price.desc())).scalars().first()
    if qimmat_kitob:
        print(f"{qimmat_kitob.title} - {qimmat_kitob.price}")

    # Eng ko‘p book yozgan authorni toping
    muallif = session.execute(select(Book.author_id).group_by(Book.author_id).order_by(func.count(Book.id).desc())).scalars().first()
    if muallif:
        print(session.get(Author, muallif).full_name)

    # Har bir authorda nechta book borligini chiqaring
    for a in session.execute(select(Author)).scalars():
        print(f"{a.full_name}: {len(a.books)} ta")

    # Book nomida "Python" so‘zi qatnashganlarini filter qiling
    for b in session.execute(select(Book).where(Book.title.like("%Python%"))).scalars():
        print(b.title)

    # Bookni author nomi bilan birga chiqaring
    for b in session.execute(select(Book)).scalars():
        print(f"{b.title} -> {b.author.full_name}")
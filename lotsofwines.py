from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Wine, Base, MenuItem

engine = create_engine('sqlite:///wine.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(username="Emma Liu", email="yunliu0212@sina.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


# Menu for white wine
wine1 = Wine(name="White Wine")

session.add(wine1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="Sauvignon blanc",
                     description="sauvignon blanc normally shows a herbal character suggesting bell pepper or freshly mown "
                         "grass. The dominating flavors range from sour green fruits of apples, pears and gooseberries "
                         "through to tropical fruits of melon, mango and blackcurrant. ",
                     location="France", taste="Sweet", wine=wine1)

session.add(menuItem2)
session.commit()


menuItem1 = MenuItem(user_id=1, name="Moscato", description="The moscato variety belongs to the muscat family of grapes - "
                                                        "and so do moscatel and muscat ottonel",
                     location="France", taste="Sweet", wine=wine1)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="Chardonnay", description="Chardonnay was the most popular white grape through the 1990s. "
                                                       "It can be made sparkling or still.",
                     location="France", taste="Sweet", wine=wine1)

session.add(menuItem2)
session.commit()

# Menu for red wine
wine2 = Wine(name="Red wine")

session.add(wine2)
session.commit()


menuItem1 = MenuItem(user_id=1, name="Merlot", description="Merlot is the Chardonnay of reds, easy to pronounce, easy to like, "
                                                   "agreeable, and versatile, but mostly lacking any substantive "
                                                   "character of its own.",
                     location="France", taste="Sweet", wine=wine2)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="Pinot Noir", description="Pinot Noir is the grape that winemakers love to hate; it is "
                                   "the prettiest, sexiest, most demanding, and least predictable of all.",
                     location="France", taste="Sweet", wine=wine2)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(user_id=1, name="Zinfandel", description="For decades Zinfandel was California grape, though now it is "
                                                      "grown all over the west coast of the United States, in "
                                                      "Australia, Italy, and elsewhere, and its ancestry has been "
                                                      "traced to Croatia.",
                     location="France", taste="Sweet", wine=wine2)
session.add(menuItem3)
session.commit()

# Menu for rose wine
wine3 = Wine(name="Rose Wine")

session.add(wine3)
session.commit()


menuItem1 = MenuItem(user_id=1, name="Grenache", description="Also known as Garnacha, the French Grenache grape is perfect "
                                                 "for producing rose wine! It is low in tannin and acidity, but "
                                                 "has decent body and lovely cherry flavours.",
                     location="France", taste="Sweet", wine=wine3)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="Syrah", description="The colour tends to be deep, usually trending more towards ruby "
                                                  "red. The rose wine has strong notes of cherries, white pepper, "
                                                  "and strawberries. It tends to be a bit more full-bodied, but a "
                                                  "good one to enjoy with food.",
                     location="France", taste="Sweet", wine=wine3)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(user_id=1, name="Tempranillo", description="Famous for being used in the red wines of Rioja, "
                                                        "it can also produce excellent rose wine.",
                     location="France", taste="Sweet", wine=wine3)

session.add(menuItem3)
session.commit()


print "added wine items!"

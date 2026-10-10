# Verification package - readable view

One section per question. Fill the CSV files, not this file. See GUIDE.md.

## musique/2hop__176_51164  (musique, 2hop, hops=2)

**Question:** When was the signing of the treaty named for the city where Beyoncé got pregnant?  
**Gold answer(s):** September 3, 1783

**Passage `musique/2hop__176_51164/p00` - Beyoncé**
- `s00` Beyoncé is believed to have first started a relationship with Jay Z after a collaboration on "'03 Bonnie & Clyde", which appeared on his seventh album The Blueprint 2: The Gift & The Curse (2002). *(gold support)*
- `s01` Beyoncé appeared as Jay Z's girlfriend in the music video for the song, which would further fuel speculation of their relationship. *(gold support)*
- `s02` On April 4, 2008, Beyoncé and Jay Z were married without publicity. *(gold support)*
- `s03` As of April 2014, the couple have sold a combined 300 million records together. *(gold support)*
- `s04` The couple are known for their private relationship, although they have appeared to become more relaxed in recent years. *(gold support)*
- `s05` Beyoncé suffered a miscarriage in 2010 or 2011, describing it as "the saddest thing" she had ever endured. *(gold support)*
- `s06` She returned to the studio and wrote music in order to cope with the loss. *(gold support)*
- `s07` In April 2011, Beyoncé and Jay Z traveled to Paris in order to shoot the album cover for her 4, and unexpectedly became pregnant in Paris. *(gold support)*

**Passage `musique/2hop__176_51164/p18` - Treaty of Paris (1783)**
- `s00` The Treaty of Paris, signed in Paris by representatives of King George III of Great Britain and representatives of the United States of America on September 3, 1783, ended the American Revolutionary War. *(gold support)*
- `s01` The treaty set the boundaries between the British Empire in North America and the United States, on lines ``exceedingly generous ''to the latter. *(gold support)*
- `s02` Details included fishing rights and restoration of property and prisoners of war. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Beyoncé - sub-question: Where did Beyoncé get pregnant? -> sub-answer: Paris.; depends on steps []
2. Treaty of Paris (1783) - sub-question: when did the treaty of #1 get signed -> sub-answer: September 3, 1783; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Paris.' exact]  `s00` "The Treaty of Paris, signed in Paris by representatives of King George III of Great Britain and representatives of the United States of America on September 3, 1783, ended the American Revolutionary War."  DEPENDS_ON  `s07` "In April 2011, Beyoncé and Jay Z traveled to Paris in order to shoot the album cover for her 4, and unexpectedly became pregnant in Paris."

---

## musique/2hop__2416_86208  (musique, 2hop, hops=2)

**Question:** When does the river that pumps the engine flood every year?  
**Gold answer(s):** August | Aug

**Passage `musique/2hop__2416_86208/p03` - Flooding of the Nile**
- `s00` The flooding of the Nile (Arabic: عيد وفاء النيل ‎, translit. eid wafa al - nayl) has been an important natural cycle in Egypt since ancient times. *(gold support)*
- `s01` It is celebrated by Egyptians as an annual holiday for two weeks starting August 15, known as Wafaa El - Nil. *(gold support)*
- `s02` It is also celebrated in the Coptic Church by ceremonially throwing a martyr's relic into the river, hence the name, The Martyr's Finger (Coptic: ⲡⲓⲧⲏⲃ ⲛⲙⲁⲣⲧⲏⲣⲟⲥ, Arabic: Esba `al - shahīd ‎). *(gold support)*
- `s03` Ancient Egyptians believed that the Nile flooded every year because of Isis's tears of sorrow for her dead husband, Osiris. *(gold support)*

**Passage `musique/2hop__2416_86208/p10` - Solar energy**
- `s00` Shuman built the world’s first solar thermal power station in Maadi, Egypt, between 1912 and 1913. *(gold support)*
- `s01` Shuman’s plant used parabolic troughs to power a 45–52 kilowatts (60–70 hp) engine that pumped more than 22,000 litres (4,800 imp gal; 5,800 US gal) of water per minute from the Nile River to adjacent cotton fields. *(gold support)*
- `s02` Although the outbreak of World War I and the discovery of cheap oil in the 1930s discouraged the advancement of solar energy, Shuman’s vision and basic design were resurrected in the 1970s with a new wave of interest in solar thermal energy. *(gold support)*
- `s03` In 1916 Shuman was quoted in the media advocating solar energy's utilization, saying: *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Solar energy - sub-question: From what river did the engine pump water? -> sub-answer: Nile River; depends on steps []
2. Flooding of the Nile - sub-question: when does #1 flood every year -> sub-answer: August; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Nile River' fallback]  `s00` "The flooding of the Nile (Arabic: عيد وفاء النيل ‎, translit. eid wafa al - nayl) has been an important natural cycle in Egypt since ancient times."  DEPENDS_ON  `s01` "Shuman’s plant used parabolic troughs to power a 45–52 kilowatts (60–70 hp) engine that pumped more than 22,000 litres (4,800 imp gal; 5,800 US gal) of water per minute from the Nile River to adjacent cotton fields."

---

## musique/3hop1__120881_2053_52946  (musique, 3hop1, hops=3)

**Question:** When is Celebrity Big Brother coming to the network which, along with ABC and the network which released Stand Against Fear, is the other major broadcaster based in NY?  
**Gold answer(s):** February 7, 2018

**Passage `musique/3hop1__120881_2053_52946/p05` - Celebrity Big Brother (American TV series)**
- `s00` Celebrity Big Brother also known as Big Brother: Celebrity Edition is a spin - off series of the American reality television series Big Brother. *(gold support)*
- `s01` This season will air during the winter of the 2017 -- 18 network television season on CBS and will be the second U.S. Big Brother season to air outside the usual summer television season, the first being Big Brother 9 in 2008. *(gold support)*
- `s02` Julie Chen will return as host, with Allison Grodner and Rich Meehan returning as executive producers. *(gold support)*
- `s03` The season will be produced by Fly on the Wall Entertainment in association with Endemol Shine North America. *(gold support)*
- `s04` CBS announced that the series is set to premiere on February 7, 2018 and conclude on February 25, 2018. *(gold support)*

**Passage `musique/3hop1__120881_2053_52946/p09` - Stand Against Fear**
- `s00` Stand Against Fear (also called Unlikely Suspects) is a 1996 American made-for-television drama film starring Sarah Chalke as a cheerleader who takes action when she faces sexual intimidation from football players at her school. *(gold support)*
- `s01` The film is a part of the "Moment of Truth" franchise and aired on NBC on December 16, 1996. *(gold support)*

**Passage `musique/3hop1__120881_2053_52946/p10` - New York City**
- `s00` The television industry developed in New York and is a significant employer in the city's economy. *(gold support)*
- `s01` The three major American broadcast networks are all headquartered in New York: ABC, CBS, and NBC. *(gold support)*
- `s02` Many cable networks are based in the city as well, including MTV, Fox News, HBO, Showtime, Bravo, Food Network, AMC, and Comedy Central. *(gold support)*
- `s03` The City of New York operates a public broadcast service, NYCTV, that has produced several original Emmy Award-winning shows covering music and culture in city neighborhoods and city government. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Stand Against Fear - sub-question: Who released Stand Against Fear? -> sub-answer: NBC; depends on steps []
2. New York City - sub-question: Along with ABC and #1 , what other major broadcaster is based in New York? -> sub-answer: CBS; depends on steps [1]
3. Celebrity Big Brother (American TV series) - sub-question: when is celebrity big brother coming to #2 -> sub-answer: February 7, 2018; depends on steps [2]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'NBC' exact]  `s01` "The three major American broadcast networks are all headquartered in New York: ABC, CBS, and NBC."  DEPENDS_ON  `s01` "The film is a part of the "Moment of Truth" franchise and aired on NBC on December 16, 1996."
- `e1` [B_derived_exact_anchor, anchor 'CBS' exact]  `s01` "This season will air during the winter of the 2017 -- 18 network television season on CBS and will be the second U.S. Big Brother season to air outside the usual summer television season, the first being Big Brother 9 in 2008."  DEPENDS_ON  `s01` "The three major American broadcast networks are all headquartered in New York: ABC, CBS, and NBC."

---

## musique/3hop1__208108_547811_41132  (musique, 3hop1, hops=3)

**Question:** How many times did plague occur in the birthplace of La Silvia's composer?  
**Gold answer(s):** 22

**Passage `musique/3hop1__208108_547811_41132/p03` - Orlando furioso (Vivaldi, 1714)**
- `s00` Orlando furioso RV 819 (, Teatro San Angelo, Venice 1714) is a three-act opera surviving in manuscript in Antonio Vivaldi's personal library, only partly related to his better known Orlando furioso (RV 728) of 1727. *(gold support)*
- `s01` It is a recomposition of an "Orlando furioso" written by Giovanni Alberto Ristori which had been very successfully staged by Vivaldi and his father's "impresa" in 1713, and whose music survives in a few fragments retained in the score of RV 819. *(gold support)*
- `s02` Therefore, Vivaldi's first cataloguer Peter Ryom did not assign the opera a RV number, but catalogued it as RV Anh. *(gold support)*
- `s03` 84. *(gold support)*
- `s04` The libretto was by Grazio Braccioli. *(gold support)*

**Passage `musique/3hop1__208108_547811_41132/p13` - Black Death**
- `s00` In 1466, perhaps 40,000 people died of the plague in Paris. *(gold support)*
- `s01` During the 16th and 17th centuries, the plague was present in Paris around 30 per cent of the time. *(gold support)*
- `s02` The Black Death ravaged Europe for three years before it continued on into Russia, where the disease was present somewhere in the country 25 times between 1350 to 1490. *(gold support)*
- `s03` Plague epidemics ravaged London in 1563, 1593, 1603, 1625, 1636, and 1665, reducing its population by 10 to 30% during those years. *(gold support)*
- `s04` Over 10% of Amsterdam's population died in 1623–25, and again in 1635–36, 1655, and 1664. *(gold support)*
- `s05` Plague occurred in Venice 22 times between 1361 and 1528. *(gold support)*
- `s06` The plague of 1576–77 killed 50,000 in Venice, almost a third of the population. *(gold support)*
- `s07` Late outbreaks in central Europe included the Italian Plague of 1629–1631, which is associated with troop movements during the Thirty Years' War, and the Great Plague of Vienna in 1679. *(gold support)*
- `s08` Over 60% of Norway's population died in 1348–50. *(gold support)*
- `s09` The last plague outbreak ravaged Oslo in 1654. *(gold support)*

**Passage `musique/3hop1__208108_547811_41132/p14` - La Silvia**
- `s00` La Silvia (RV 734) is an "dramma pastorale per musica" in three acts by Antonio Vivaldi to an Italian libretto by Enrico Bissari. *(gold support)*
- `s01` It was first performed on 28 August 1721 at the Teatro Regio Ducale in Milan on the occasion of the birthday celebrations of the Austrian Empress Elisabeth Christine, wife of Emperor Charles VI of Austria. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. La Silvia - sub-question: La Silvia >> composer -> sub-answer: Antonio Vivaldi; depends on steps []
2. Orlando furioso (Vivaldi, 1714) - sub-question: #1 >> place of birth -> sub-answer: Venice; depends on steps [1]
3. Black Death - sub-question: How many times did plague occur in #2 ? -> sub-answer: 22; depends on steps [2]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Antonio Vivaldi' fallback]  `s00` "Orlando furioso RV 819 (, Teatro San Angelo, Venice 1714) is a three-act opera surviving in manuscript in Antonio Vivaldi's personal library, only partly related to his better known Orlando furioso (RV 728) of 1727."  DEPENDS_ON  `s00` "La Silvia (RV 734) is an "dramma pastorale per musica" in three acts by Antonio Vivaldi to an Italian libretto by Enrico Bissari."
- `e1` [B_derived_exact_anchor, anchor 'Venice' exact]  `s05` "Plague occurred in Venice 22 times between 1361 and 1528."  DEPENDS_ON  `s00` "Orlando furioso RV 819 (, Teatro San Angelo, Venice 1714) is a three-act opera surviving in manuscript in Antonio Vivaldi's personal library, only partly related to his better known Orlando furioso (RV 728) of 1727."

---

## musique/4hop1__15567_59747_211319_557671  (musique, 4hop1, hops=4)

**Question:** Which county shares a border with the county where the most populous city in the state that sentenced Demarcus Sears to death is located?  
**Gold answer(s):** Presque Isle County

**Passage `musique/4hop1__15567_59747_211319_557671/p03` - Sno*Drift**
- `s00` Sno*Drift is a rally racing event held in Montmorency County, Michigan, annually, with headquarters in Atlanta, Michigan. *(gold support)*
- `s01` The event is currently the first Rally America National Rally Championship event of the season. *(gold support)*
- `s02` Currently the event is organized into three distinct rallies: the national championship event covering both days of rallying, and two regional rally events each covering one of the two days. *(gold support)*
- `s03` Competitors may be entered in any or all of these events simultaneously. *(gold support)*

**Passage `musique/4hop1__15567_59747_211319_557671/p07` - List of municipalities in Georgia (U.S. state)**
- `s00` The largest municipality by population in Georgia is Atlanta with 420,003 residents, and the smallest municipality by population is Edge Hill with 24 residents. *(gold support)*
- `s01` The largest municipality by land area is Augusta, a consolidated city - county, which spans 302.47 sq mi (783.4 km), while Edge Hill and Santa Claus are tied for the smallest at 0.18 sq mi (0.47 km) each. *(gold support)*

**Passage `musique/4hop1__15567_59747_211319_557671/p12` - Alpena Power Company**
- `s00` Alpena Power Company is a public utility company that provides electricity to most of Alpena County, Michigan, as well as southeastern Presque Isle County and the village of Hillman, in Montmorency County. *(gold support)*
- `s01` The headquarters are located in Alpena, Michigan. *(gold support)*
- `s02` The company was founded in 1881 by George N. Fletcher. *(gold support)*

**Passage `musique/4hop1__15567_59747_211319_557671/p14` - Capital punishment in the United States**
- `s00` As of November 2008, there is only one person on death row facing capital punishment who has not been convicted of murder. *(gold support)*
- `s01` Demarcus Sears remains under a death sentence in Georgia for the crime of "kidnapping with bodily injury." *(gold support)*
- `s02` Sears was convicted in 1986 for the kidnapping and bodily injury of victim Gloria Ann Wilbur. *(gold support)*
- `s03` Wilbur was kidnapped and beaten in Georgia, raped in Tennessee, and murdered in Kentucky. *(gold support)*
- `s04` Sears was never charged with the murder of Wilbur in Kentucky, but was sentenced to death by a jury in Georgia for "kidnapping with bodily injury." *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Capital punishment in the United States - sub-question: A jury in what state sentenced Demarcus Sears to death? -> sub-answer: Georgia; depends on steps []
2. List of municipalities in Georgia (U.S. state) - sub-question: what is the largest city in #1 by population -> sub-answer: Atlanta; depends on steps [1]
3. Sno*Drift - sub-question: #2 >> located in the administrative territorial entity -> sub-answer: Montmorency County; depends on steps [2]
4. Alpena Power Company - sub-question: #3 >> shares border with -> sub-answer: Presque Isle County; depends on steps [3]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Georgia' exact]  `s00` "The largest municipality by population in Georgia is Atlanta with 420,003 residents, and the smallest municipality by population is Edge Hill with 24 residents."  DEPENDS_ON  `s01` "Demarcus Sears remains under a death sentence in Georgia for the crime of "kidnapping with bodily injury.""
- `e1` [B_derived_exact_anchor, anchor 'Atlanta' exact]  `s00` "Sno*Drift is a rally racing event held in Montmorency County, Michigan, annually, with headquarters in Atlanta, Michigan."  DEPENDS_ON  `s00` "The largest municipality by population in Georgia is Atlanta with 420,003 residents, and the smallest municipality by population is Edge Hill with 24 residents."
- `e2` [B_derived_exact_anchor, anchor 'Montmorency County' exact]  `s00` "Alpena Power Company is a public utility company that provides electricity to most of Alpena County, Michigan, as well as southeastern Presque Isle County and the village of Hillman, in Montmorency County."  DEPENDS_ON  `s00` "Sno*Drift is a rally racing event held in Montmorency County, Michigan, annually, with headquarters in Atlanta, Michigan."

---

## musique/4hop1__88342_75218_128008_46894  (musique, 4hop1, hops=4)

**Question:** Who had the lowest batting average in the league where the team with the most games in the series after which the MLB MVP is awarded played?  
**Gold answer(s):** Bill Bergen

**Passage `musique/4hop1__88342_75218_128008_46894/p01` - New York Yankees**
- `s00` The New York Yankees are an American professional baseball team based in the New York City borough of the Bronx. *(gold support)*
- `s01` The Yankees compete in Major League Baseball (MLB) as a member club of the American League (AL) East division. *(gold support)*
- `s02` They are one of two major league clubs based in New York City; the other club is the National League (NL)'s New York Mets. *(gold support)*
- `s03` In the season, the club began play in the AL as the Baltimore Orioles (no relation to the modern Baltimore Orioles). *(gold support)*
- `s04` Frank Farrell and Bill Devery purchased the franchise that had ceased operations and moved it to New York City, renaming the club the New York Highlanders. *(gold support)*
- `s05` The Highlanders were officially renamed the Yankees in . *(gold support)*

**Passage `musique/4hop1__88342_75218_128008_46894/p09` - Batting average**
- `s00` Ty Cobb holds the record for highest career batting average with. *(gold support)*
- `s01` 366, 9 points higher than Rogers Hornsby who has the second highest average in history at. *(gold support)*
- `s02` 358. *(gold support)*
- `s03` The record for lowest career batting average for a player with more than 2,500 at - bats belongs to Bill Bergen, a catcher who played from 1901 to 1911 and recorded a. 170 average in 3,028 career at - bats. *(gold support)*
- `s04` The modern - era record for highest batting average for a season is held by Napoleon Lajoie, who hit. *(gold support)*
- `s05` 426 in 1901, the first year of play for the American League. *(gold support)*
- `s06` The modern - era record for lowest batting average for a player that qualified for the batting title is held by Rob Deer, who hit. *(gold support)*
- `s07` 179 in 1991. *(gold support)*
- `s08` While finishing six plate appearances short of qualifying for the batting title, Adam Dunn of the Chicago White Sox hit. *(gold support)*
- `s09` 159 for the 2011 season, twenty points (and 11.2%) lower than the record. *(gold support)*
- `s10` The highest batting average for a rookie was. *(gold support)*
- `s11` 408 in 1911 by Shoeless Joe Jackson. *(gold support)*

**Passage `musique/4hop1__88342_75218_128008_46894/p11` - Major League Baseball Most Valuable Player Award**
- `s00` MVP voting takes place before the postseason, but the results are not announced until after the World Series. *(gold support)*
- `s01` The BBWAA began by polling three writers in each league city in 1938, reducing that number to two per league city in 1961. *(gold support)*
- `s02` The BBWAA does not offer a clear - cut definition of what ``most valuable ''means, instead leaving the judgment to the individual voters. *(gold support)*

**Passage `musique/4hop1__88342_75218_128008_46894/p17` - World Series**
- `s00` In the American League, the New York Yankees have played in 40 World Series and won 27, the Philadelphia / Kansas City / Oakland Athletics have played in 14 and won 9, and the Boston Red Sox have played in 12 and won 8, including the first World Series. *(gold support)*
- `s01` In the National League, the St. Louis Cardinals have appeared in 19 and won 11, the New York / San Francisco Giants have played in 20 and won 8, the Brooklyn / Los Angeles Dodgers have appeared in 19 and won 6, and the Cincinnati Reds have appeared in 9 and won 5. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Major League Baseball Most Valuable Player Award - sub-question: when do they give out the mlb mvp award -> sub-answer: after the World Series; depends on steps []
2. World Series - sub-question: who played in the most #1 games -> sub-answer: the New York Yankees; depends on steps [1]
3. New York Yankees - sub-question: Which is the league of #2 ? -> sub-answer: Major League Baseball; depends on steps [2]
4. Batting average - sub-question: who has the lowest batting average in #3 -> sub-answer: Bill Bergen; depends on steps [3]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'after the World Series' fallback]  `s00` "In the American League, the New York Yankees have played in 40 World Series and won 27, the Philadelphia / Kansas City / Oakland Athletics have played in 14 and won 9, and the Boston Red Sox have played in 12 and won 8, including the first World Series."  DEPENDS_ON  `s00` "MVP voting takes place before the postseason, but the results are not announced until after the World Series."
- `e1` [B_derived_exact_anchor, anchor 'the New York Yankees' exact]  `s00` "The New York Yankees are an American professional baseball team based in the New York City borough of the Bronx."  DEPENDS_ON  `s00` "In the American League, the New York Yankees have played in 40 World Series and won 27, the Philadelphia / Kansas City / Oakland Athletics have played in 14 and won 9, and the Boston Red Sox have played in 12 and won 8, including the first World Series."
- `e2` [C_derived_fallback_anchor, anchor 'Major League Baseball' fallback]  `s00` "Ty Cobb holds the record for highest career batting average with."  DEPENDS_ON  `s01` "The Yankees compete in Major League Baseball (MLB) as a member club of the American League (AL) East division."

---

## musique/2hop__486392_35739  (musique, 2hop, hops=2)

**Question:** When was the version of Windows 8 from the company that Iceweasel was based on made accessible?  
**Gold answer(s):** September 2013

**Passage `musique/2hop__486392_35739/p05` - Windows 8**
- `s00` The developers of both Chrome and Firefox committed to developing Metro-style versions of their browsers; while Chrome's "Windows 8 mode" uses a full-screen version of the existing desktop interface, Firefox's version (which was first made available on the "Aurora" release channel in September 2013) uses a touch-optimized interface inspired by the Android version of Firefox. *(gold support)*
- `s01` In October 2013, Chrome's app was changed to mimic the desktop environment used by Chrome OS. *(gold support)*
- `s02` Development of the Firefox app for Windows 8 has since been cancelled, citing a lack of user adoption for the beta versions. *(gold support)*

**Passage `musique/2hop__486392_35739/p10` - GNU IceCat**
- `s00` GNU IceCat, formerly known as GNU IceWeasel, is a free software rebranding of the Mozilla Firefox web browser distributed by the GNU Project. *(gold support)*
- `s01` It is compatible with GNU/Linux, Windows, Android and macOS. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. GNU IceCat - sub-question: Iceweasel >> based on -> sub-answer: Firefox; depends on steps []
2. Windows 8 - sub-question: When was #1 's version of Windows 8 made accesible? -> sub-answer: September 2013; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Firefox' exact]  `s00` "The developers of both Chrome and Firefox committed to developing Metro-style versions of their browsers; while Chrome's "Windows 8 mode" uses a full-screen version of the existing desktop interface, Firefox's version (which was first made available on the "Aurora" release channel in September 2013) uses a touch-optimized interface inspired by the Android version of Firefox."  DEPENDS_ON  `s00` "GNU IceCat, formerly known as GNU IceWeasel, is a free software rebranding of the Mozilla Firefox web browser distributed by the GNU Project."

---

## musique/2hop__20256_71302  (musique, 2hop, hops=2)

**Question:** In The Godfather, who does the actor producing the Freddie Mercury film play?  
**Gold answer(s):** Vito Corleone | Vito Andolini | Vito Andolini Corleone

**Passage `musique/2hop__20256_71302/p03` - Queen (band)**
- `s00` In September 2010, Brian May announced in a BBC interview that Sacha Baron Cohen was to play Mercury in a film of the same name. *(gold support)*
- `s01` Time commented with approval on his singing ability and visual similarity to Mercury. *(gold support)*
- `s02` However, in July 2013, Baron Cohen dropped out of the role due to "creative differences" between him and the surviving band members. *(gold support)*
- `s03` In December 2013, it was announced that Ben Whishaw, best known for playing Q in the James Bond film Skyfall, had been chosen to replace Cohen in the role of Mercury. *(gold support)*
- `s04` The motion picture is being written by Peter Morgan, who had been nominated for Oscars for his screenplays The Queen and Frost/Nixon. *(gold support)*
- `s05` The film, which is being co-produced by Robert De Niro's TriBeCa Productions, will focus on Queen's formative years and the period leading up to the celebrated performance at the 1985 Live Aid concert. *(gold support)*

**Passage `musique/2hop__20256_71302/p18` - The Godfather Part II**
- `s00` The Godfather Part II is a 1974 American crime film produced and directed by Francis Ford Coppola from a screenplay co-written with Mario Puzo, starring Al Pacino and Robert De Niro. *(gold support)*
- `s01` Partially based on Puzo's 1969 novel The Godfather, the film is both sequel and prequel to The Godfather, presenting parallel dramas: one picks up the 1958 story of Michael Corleone (Pacino), the new Don of the Corleone crime family, protecting the family business in the aftermath of an attempt on his life; the prequel covers the journey of his father, Vito Corleone (De Niro), from his Sicilian childhood to the founding of his family enterprise in New York City. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Queen (band) - sub-question: Which actor is producing the Freddie Mercury film? -> sub-answer: Robert De Niro; depends on steps []
2. The Godfather Part II - sub-question: who does #1 play in the godfather -> sub-answer: Vito Corleone; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Robert De Niro' fallback]  `s00` "The Godfather Part II is a 1974 American crime film produced and directed by Francis Ford Coppola from a screenplay co-written with Mario Puzo, starring Al Pacino and Robert De Niro."  DEPENDS_ON  `s00` "In September 2010, Brian May announced in a BBC interview that Sacha Baron Cohen was to play Mercury in a film of the same name."

---

## musique/3hop1__152880_131926_89261  (musique, 3hop1, hops=3)

**Question:** Where does the body of water by the city that Astronautalis is from empty into the gulf of Mexico?  
**Gold answer(s):** the Mississippi River Delta | Mississippi River Delta

**Passage `musique/3hop1__152880_131926_89261/p06` - Mississippi River**
- `s00` The Mississippi River is the chief river of the second - largest drainage system on the North American continent, second only to the Hudson Bay drainage system. *(gold support)*
- `s01` Flowing entirely in the United States (although its drainage basin reaches into Canada), it rises in northern Minnesota and meanders slowly southwards for 2,320 miles (3,730 km) to the Mississippi River Delta at the Gulf of Mexico. *(gold support)*
- `s02` With its many tributaries, the Mississippi's watershed drains all or parts of 31 U.S. states and 2 Canadian provinces between the Rocky and Appalachian Mountains. *(gold support)*
- `s03` The Mississippi ranks as the fourth - longest and fifteenth - largest river in the world by discharge. *(gold support)*
- `s04` The river either borders or passes through the states of Minnesota, Wisconsin, Iowa, Illinois, Missouri, Kentucky, Tennessee, Arkansas, Mississippi, and Louisiana. *(gold support)*

**Passage `musique/3hop1__152880_131926_89261/p08` - Minneapolis**
- `s00` Minneapolis lies on both banks of the Mississippi River, just north of the river's confluence with the Minnesota River, and adjoins Saint Paul, the state's capital. *(gold support)*
- `s01` The city is abundantly rich in water, with 13 lakes, wetlands, the Mississippi River, creeks and waterfalls; many connected by parkways in the Chain of Lakes and the Grand Rounds National Scenic Byway. *(gold support)*
- `s02` It was once the world's flour milling capital and a hub for timber. *(gold support)*
- `s03` The city and surrounding region is the primary business center between Chicago and Seattle. *(gold support)*
- `s04` As of 2018, Minneapolis was home to 6 Fortune 500 companies, and the Twin Cities were the fifth-largest hub of major corporate headquarters in the United States. *(gold support)*
- `s05` As an integral link to the global economy, Minneapolis is categorized as a global city. *(gold support)*

**Passage `musique/3hop1__152880_131926_89261/p14` - Astronautalis**
- `s00` Charles Andrew Bothwell (born December 13, 1981), known by his stage name 'Astronautalis', is an American alternative hip hop artist currently based in Minneapolis, Minnesota. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Astronautalis - sub-question: What city is Astronautalis from? -> sub-answer: Minneapolis; depends on steps []
2. Minneapolis - sub-question: Which is the body of water by #1 ? -> sub-answer: Mississippi River; depends on steps [1]
3. Mississippi River - sub-question: where does #2 empty into the gulf of mexico -> sub-answer: the Mississippi River Delta; depends on steps [2]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Minneapolis' exact]  `s00` "Minneapolis lies on both banks of the Mississippi River, just north of the river's confluence with the Minnesota River, and adjoins Saint Paul, the state's capital."  DEPENDS_ON  `s00` "Charles Andrew Bothwell (born December 13, 1981), known by his stage name 'Astronautalis', is an American alternative hip hop artist currently based in Minneapolis, Minnesota."
- `e1` [B_derived_exact_anchor, anchor 'Mississippi River' exact]  `s00` "The Mississippi River is the chief river of the second - largest drainage system on the North American continent, second only to the Hudson Bay drainage system."  DEPENDS_ON  `s00` "Minneapolis lies on both banks of the Mississippi River, just north of the river's confluence with the Minnesota River, and adjoins Saint Paul, the state's capital."

---

## musique/3hop1__280834_547811_41132  (musique, 3hop1, hops=3)

**Question:** How many times did plague occur in the place where Bajazet's composer was born?  
**Gold answer(s):** 22

**Passage `musique/3hop1__280834_547811_41132/p04` - Orlando furioso (Vivaldi, 1714)**
- `s00` Orlando furioso RV 819 (, Teatro San Angelo, Venice 1714) is a three-act opera surviving in manuscript in Antonio Vivaldi's personal library, only partly related to his better known Orlando furioso (RV 728) of 1727. *(gold support)*
- `s01` It is a recomposition of an "Orlando furioso" written by Giovanni Alberto Ristori which had been very successfully staged by Vivaldi and his father's "impresa" in 1713, and whose music survives in a few fragments retained in the score of RV 819. *(gold support)*
- `s02` Therefore, Vivaldi's first cataloguer Peter Ryom did not assign the opera a RV number, but catalogued it as RV Anh. *(gold support)*
- `s03` 84. *(gold support)*
- `s04` The libretto was by Grazio Braccioli. *(gold support)*

**Passage `musique/3hop1__280834_547811_41132/p09` - Black Death**
- `s00` In 1466, perhaps 40,000 people died of the plague in Paris. *(gold support)*
- `s01` During the 16th and 17th centuries, the plague was present in Paris around 30 per cent of the time. *(gold support)*
- `s02` The Black Death ravaged Europe for three years before it continued on into Russia, where the disease was present somewhere in the country 25 times between 1350 to 1490. *(gold support)*
- `s03` Plague epidemics ravaged London in 1563, 1593, 1603, 1625, 1636, and 1665, reducing its population by 10 to 30% during those years. *(gold support)*
- `s04` Over 10% of Amsterdam's population died in 1623–25, and again in 1635–36, 1655, and 1664. *(gold support)*
- `s05` Plague occurred in Venice 22 times between 1361 and 1528. *(gold support)*
- `s06` The plague of 1576–77 killed 50,000 in Venice, almost a third of the population. *(gold support)*
- `s07` Late outbreaks in central Europe included the Italian Plague of 1629–1631, which is associated with troop movements during the Thirty Years' War, and the Great Plague of Vienna in 1679. *(gold support)*
- `s08` Over 60% of Norway's population died in 1348–50. *(gold support)*
- `s09` The last plague outbreak ravaged Oslo in 1654. *(gold support)*

**Passage `musique/3hop1__280834_547811_41132/p12` - Bajazet (opera)**
- `s00` Bajazet (; also called "Il Tamerlano") is an Italian opera composed by Antonio Vivaldi in 1735. *(gold support)*
- `s01` Its libretto was written by Agostino Piovene. *(gold support)*
- `s02` It was premiered in Verona, during the Carnival season of that year. *(gold support)*
- `s03` This opera (catalog number RV 703) is presented in 3 acts, with a three-movement sinfonia as an introduction. *(gold support)*
- `s04` The story is about the fate of Bajazet (known as Beyazid I) after being captured by Tamerlane (Timur Lenk). *(gold support)*
- `s05` The famous aria, "Sposa son disprezzata" is from this opera. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Bajazet (opera) - sub-question: Bajazet >> composer -> sub-answer: Antonio Vivaldi; depends on steps []
2. Orlando furioso (Vivaldi, 1714) - sub-question: #1 >> place of birth -> sub-answer: Venice; depends on steps [1]
3. Black Death - sub-question: How many times did plague occur in #2 ? -> sub-answer: 22; depends on steps [2]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Antonio Vivaldi' fallback]  `s00` "Orlando furioso RV 819 (, Teatro San Angelo, Venice 1714) is a three-act opera surviving in manuscript in Antonio Vivaldi's personal library, only partly related to his better known Orlando furioso (RV 728) of 1727."  DEPENDS_ON  `s00` "Bajazet (; also called "Il Tamerlano") is an Italian opera composed by Antonio Vivaldi in 1735."
- `e1` [B_derived_exact_anchor, anchor 'Venice' exact]  `s05` "Plague occurred in Venice 22 times between 1361 and 1528."  DEPENDS_ON  `s00` "Orlando furioso RV 819 (, Teatro San Angelo, Venice 1714) is a three-act opera surviving in manuscript in Antonio Vivaldi's personal library, only partly related to his better known Orlando furioso (RV 728) of 1727."

---

## musique/4hop1__152146_5274_458768_33677  (musique, 4hop1, hops=4)

**Question:** When was the most recent Bicycle Friendly Community Award given to the city where the headquarters of the only group larger than Långa nätter's record label is located?  
**Gold answer(s):** 2013

**Passage `musique/4hop1__152146_5274_458768_33677/p04` - Sony Music**
- `s00` Sony Music Entertainment Inc. (sometimes known as Sony Music or by the initials, SME) is an American music corporation managed and operated by Sony Corporation of America (SCA), a subsidiary of Japanese conglomerate Sony Corporation. *(gold support)*
- `s01` In 1929, the enterprise was first founded as American Record Corporation (ARC) and, in 1938, was renamed Columbia Recording Corporation, following ARC's acquisition by CBS. *(gold support)*
- `s02` In 1966, the company was reorganized to become CBS Records. *(gold support)*
- `s03` In 1987, Sony Corporation of Japan bought the company, and in 1991, renamed it SME. *(gold support)*
- `s04` It is the world's second largest recorded music company, after Universal Music Group. *(gold support)*

**Passage `musique/4hop1__152146_5274_458768_33677/p05` - Långa nätter**
- `s00` Långa nätter is the debut album by singer-songwriter Melissa Horn, released April 30, 2008, on Sony Music Entertainment. *(gold support)*
- `s01` It was produced by Lasse Englund and Jan Radesjö. *(gold support)*
- `s02` The album features the singles "Långa nätter", "En famn för mig" and "Som jag hade dig förut", a duet with Lars Winnerbäck. *(gold support)*

**Passage `musique/4hop1__152146_5274_458768_33677/p14` - The Right Stuff Records**
- `s00` The Right Stuff Records is a reissue record label that was part of EMI, which is now owned by Universal Music Group and is based out of Santa Monica, California. *(gold support)*

**Passage `musique/4hop1__152146_5274_458768_33677/p16` - Santa Monica, California**
- `s00` Santa Monica has a bike action plan and recently launched a Bicycle sharing system in November 2015. *(gold support)*
- `s01` The city is traversed by the Marvin Braude Bike Trail. *(gold support)*
- `s02` Santa Monica has received the Bicycle Friendly Community Award (Bronze in 2009, Silver in 2013) by the League of American Bicyclists. *(gold support)*
- `s03` Local bicycle advocacy organizations include Santa Monica Spoke, a local chapter of the Los Angeles County Bicycle Coalition. *(gold support)*
- `s04` Santa Monica is thought to be one of the leaders for bicycle infrastructure and programming in Los Angeles County.[citation needed] *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Långa nätter - sub-question: What was the record label of Långa nätter? -> sub-answer: Sony Music Entertainment; depends on steps []
2. Sony Music - sub-question: What company is the only group larger than #1 ? -> sub-answer: Universal Music Group.; depends on steps [1]
3. The Right Stuff Records - sub-question: #2 >> headquarters location -> sub-answer: Santa Monica; depends on steps [2]
4. Santa Monica, California - sub-question: When was the most recent Bicycle Friendly Community Award given to #3 ? -> sub-answer: 2013; depends on steps [3]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Sony Music Entertainment' exact]  `s00` "Sony Music Entertainment Inc. (sometimes known as Sony Music or by the initials, SME) is an American music corporation managed and operated by Sony Corporation of America (SCA), a subsidiary of Japanese conglomerate Sony Corporation."  DEPENDS_ON  `s00` "Långa nätter is the debut album by singer-songwriter Melissa Horn, released April 30, 2008, on Sony Music Entertainment."
- `e1` [B_derived_exact_anchor, anchor 'Universal Music Group.' exact]  `s00` "The Right Stuff Records is a reissue record label that was part of EMI, which is now owned by Universal Music Group and is based out of Santa Monica, California."  DEPENDS_ON  `s04` "It is the world's second largest recorded music company, after Universal Music Group."
- `e2` [B_derived_exact_anchor, anchor 'Santa Monica' exact]  `s00` "Santa Monica has a bike action plan and recently launched a Bicycle sharing system in November 2015."  DEPENDS_ON  `s00` "The Right Stuff Records is a reissue record label that was part of EMI, which is now owned by Universal Music Group and is based out of Santa Monica, California."

---

## musique/4hop1__277409_49925_13759_736921  (musique, 4hop1, hops=4)

**Question:** The German priest, who wanted Joseph Strickland's religious denomination to reform, preached a sermon on Marian devotion soon before his death in what German state?  
**Gold answer(s):** Saxony-Anhalt

**Passage `musique/4hop1__277409_49925_13759_736921/p05` - Mary, mother of Jesus**
- `s00` Despite Martin Luther's harsh polemics against his Roman Catholic opponents over issues concerning Mary and the saints, theologians appear to agree that Luther adhered to the Marian decrees of the ecumenical councils and dogmas of the church. *(gold support)*
- `s01` He held fast to the belief that Mary was a perpetual virgin and the Theotokos or Mother of God. *(gold support)*
- `s02` Special attention is given to the assertion that Luther, some three-hundred years before the dogmatization of the Immaculate Conception by Pope Pius IX in 1854, was a firm adherent of that view. *(gold support)*
- `s03` Others maintain that Luther in later years changed his position on the Immaculate Conception, which, at that time was undefined in the Church, maintaining however the sinlessness of Mary throughout her life. *(gold support)*
- `s04` For Luther, early in his life, the Assumption of Mary was an understood fact, although he later stated that the Bible did not say anything about it and stopped celebrating its feast. *(gold support)*
- `s05` Important to him was the belief that Mary and the saints do live on after death. *(gold support)*
- `s06` "Throughout his career as a priest-professor-reformer, Luther preached, taught, and argued about the veneration of Mary with a verbosity that ranged from childlike piety to sophisticated polemics. *(gold support)*
- `s07` His views are intimately linked to his Christocentric theology and its consequences for liturgy and piety." *(gold support)*
- `s08` Luther, while revering Mary, came to criticize the "Papists" for blurring the line, between high admiration of the grace of God wherever it is seen in a human being, and religious service given to another creature. *(gold support)*
- `s09` He considered the Roman Catholic practice of celebrating saints' days and making intercessory requests addressed especially to Mary and other departed saints to be idolatry. *(gold support)*
- `s10` His final thoughts on Marian devotion and veneration are preserved in a sermon preached at Wittenberg only a month before his death: *(gold support)*

**Passage `musique/4hop1__277409_49925_13759_736921/p15` - Joseph Strickland**
- `s00` Joseph Edward Strickland (born October 31, 1958) is an American prelate of the Catholic Church. *(gold support)*
- `s01` Known affectionately by many of his longtime parishioners as Bishop Joe, since his consecration on November 28, 2012, he has been the Bishop of the Roman Catholic Diocese of Tyler. *(gold support)*

**Passage `musique/4hop1__277409_49925_13759_736921/p16` - Reformation**
- `s00` Although there had been significant earlier attempts to reform the Catholic Church before Luther -- such as those of Jan Hus, Peter Waldo, and John Wycliffe -- Martin Luther is widely acknowledged to have started the Reformation with the Ninety - five Theses. *(gold support)*
- `s01` Luther began by criticising the sale of indulgences, insisting that the Pope had no authority over purgatory and that the Catholic doctrine of the merits of the saints had no foundation in the Bible. *(gold support)*
- `s02` The Protestant Reformation, however, would come to incorporate doctrinal changes such as a complete reliance on Scripture as a source of proper belief (sola scriptura) and the belief that faith in Jesus, and not good works, is the only way to obtain God's pardon for sin (sola fide). *(gold support)*
- `s03` The core motivation behind these changes was theological, though many other factors played a part, including the rise of nationalism, the Western Schism that eroded loyalty to the Papacy, the perceived corruption of the Roman Curia, the impact of humanism, and the new learning of the Renaissance that questioned much traditional thought. *(gold support)*

**Passage `musique/4hop1__277409_49925_13759_736921/p19` - Wittenberg (district)**
- `s00` Wittenberg is a district () in the east of Saxony-Anhalt, Germany. *(gold support)*
- `s01` Neighboring districts are (from west clockwise) Anhalt-Bitterfeld, the district-free city of Dessau-Roßlau, the districts of Potsdam-Mittelmark, Teltow-Fläming and Elbe-Elster in Brandenburg, and the district of Nordsachsen in the Free State of Saxony. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Joseph Strickland - sub-question: Joseph Strickland >> religion -> sub-answer: Catholic Church; depends on steps []
2. Reformation - sub-question: who wanted #1 to reform and address -> sub-answer: Martin Luther; depends on steps [1]
3. Mary, mother of Jesus - sub-question: Where did #2 preach a sermon on Marian devotion a month before his death? -> sub-answer: Wittenberg; depends on steps [2]
4. Wittenberg (district) - sub-question: #3 >> located in the administrative territorial entity -> sub-answer: Saxony-Anhalt; depends on steps [3]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Catholic Church' exact]  `s00` "Although there had been significant earlier attempts to reform the Catholic Church before Luther -- such as those of Jan Hus, Peter Waldo, and John Wycliffe -- Martin Luther is widely acknowledged to have started the Reformation with the Ninety - five Theses."  DEPENDS_ON  `s00` "Joseph Edward Strickland (born October 31, 1958) is an American prelate of the Catholic Church."
- `e1` [C_derived_fallback_anchor, anchor 'Martin Luther' fallback]  `s00` "Despite Martin Luther's harsh polemics against his Roman Catholic opponents over issues concerning Mary and the saints, theologians appear to agree that Luther adhered to the Marian decrees of the ecumenical councils and dogmas of the church."  DEPENDS_ON  `s00` "Although there had been significant earlier attempts to reform the Catholic Church before Luther -- such as those of Jan Hus, Peter Waldo, and John Wycliffe -- Martin Luther is widely acknowledged to have started the Reformation with the Ninety - five Theses."
- `e2` [B_derived_exact_anchor, anchor 'Wittenberg' exact]  `s00` "Wittenberg is a district () in the east of Saxony-Anhalt, Germany."  DEPENDS_ON  `s10` "His final thoughts on Marian devotion and veneration are preserved in a sermon preached at Wittenberg only a month before his death:"

---

## musique/2hop__43776_162341  (musique, 2hop, hops=2)

**Question:** What other recognition did the Oscar winner for Best Actor in 2006 receive?  
**Gold answer(s):** nominated for an Academy Award for Best Supporting Actor | Academy Award for Best Supporting Actor

**Passage `musique/2hop__43776_162341/p05` - Charlie Wilson's War (film)**
- `s00` The film was directed by Mike Nichols (his final film) and written by Aaron Sorkin, who adapted George Crile III's 2003 book Charlie Wilson's War: The Extraordinary Story of the Largest Covert Operation in History. *(gold support)*
- `s01` Tom Hanks, Julia Roberts, and Philip Seymour Hoffman starred, with Amy Adams and Ned Beatty in supporting roles. *(gold support)*
- `s02` It was nominated for five Golden Globe Awards, including Best Motion Picture – Musical or Comedy, but did not win in any category. *(gold support)*
- `s03` Hoffman was nominated for an Academy Award for Best Supporting Actor. *(gold support)*

**Passage `musique/2hop__43776_162341/p12` - 78th Academy Awards**
- `s00` Philip Seymour Hoffman -- Capote as Truman Capote Terrence Howard -- Hustle & Flow as DJay Heath Ledger -- Brokeback Mountain as Ennis Del Mar Joaquin Phoenix -- Walk the Line as Johnny Cash David Strathairn -- Good Night, and Good Luck as Edward R. Murrow *(gold support)*

**Proposed reasoning steps (dataset order):**
1. 78th Academy Awards - sub-question: who won the oscar for best actor in 2006 -> sub-answer: Philip Seymour Hoffman; depends on steps []
2. Charlie Wilson's War (film) - sub-question: #1 received what recognition? -> sub-answer: nominated for an Academy Award for Best Supporting Actor; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Philip Seymour Hoffman' exact]  `s01` "Tom Hanks, Julia Roberts, and Philip Seymour Hoffman starred, with Amy Adams and Ned Beatty in supporting roles."  DEPENDS_ON  `s00` "Philip Seymour Hoffman -- Capote as Truman Capote Terrence Howard -- Hustle & Flow as DJay Heath Ledger -- Brokeback Mountain as Ennis Del Mar Joaquin Phoenix -- Walk the Line as Johnny Cash David Strathairn -- Good Night, and Good Luck as Edward R. Murrow"

---

## musique/2hop__58691_192417  (musique, 2hop, hops=2)

**Question:** The league playing in the Thursday night football game is a type of what?  
**Gold answer(s):** sports league | Sports league | league

**Passage `musique/2hop__58691_192417/p00` - Thursday Night Football**
- `s00` Thursday Night Football (or simply TNF) is the branding used for broadcasts of National Football League (NFL) games that broadcast primarily on Thursday nights. *(gold support)*
- `s01` Most of the games kick off at 8: 25 p.m. *(gold support)*
- `s02` Eastern Time, but games in the package also air occasionally on Saturdays in the later portion of the season, as well as a single Sunday morning game from London in the NFL International Series (these games have been branded since 2017 as NFL Network Special). *(gold support)*

**Passage `musique/2hop__58691_192417/p05` - Sports league ranking**
- `s00` In a sports league, the ranking of a team is the place where it is within the division. *(gold support)*
- `s01` Generally, ranking is based on won-lost record of games, with the team with the best record at the top, and the worst record at the bottom. *(gold support)*
- `s02` Another common method is a points-based ranking system, where a team is awarded a certain number of points per win, fewer points per tie, and none for a loss. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Thursday Night Football - sub-question: who plays in the thursday night football game -> sub-answer: National Football League; depends on steps []
2. Sports league ranking - sub-question: #1 >> instance of -> sub-answer: sports league; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'National Football League' fallback]  `s00` "In a sports league, the ranking of a team is the place where it is within the division."  DEPENDS_ON  `s00` "Thursday Night Football (or simply TNF) is the branding used for broadcasts of National Football League (NFL) games that broadcast primarily on Thursday nights."

---

## musique/3hop1__186307_503371_21711  (musique, 3hop1, hops=3)

**Question:** When was the Palau de la Generalitat constructed in the city where Martin from where Jaulin is located died?  
**Gold answer(s):** built in the 15th century | 15th century

**Passage `musique/3hop1__186307_503371_21711/p00` - Gothic architecture**
- `s00` The Palais des Papes in Avignon is the best complete large royal palace, alongside the Royal palace of Olite, built during the 13th and 14th centuries for the kings of Navarre. *(gold support)*
- `s01` The Malbork Castle built for the master of the Teutonic order is an example of Brick Gothic architecture. *(gold support)*
- `s02` Partial survivals of former royal residences include the Doge's Palace of Venice, the Palau de la Generalitat in Barcelona, built in the 15th century for the kings of Aragon, or the famous Conciergerie, former palace of the kings of France, in Paris. *(gold support)*

**Passage `musique/3hop1__186307_503371_21711/p07` - Jaulín**
- `s00` Jaulín is a municipality located in the province of Zaragoza, Aragon, Spain. *(gold support)*
- `s01` According to the 2004 census (INE), the municipality has a population of 307 inhabitants. *(gold support)*

**Passage `musique/3hop1__186307_503371_21711/p09` - Martin of Aragon**
- `s00` Martin the Humane (29 July 1356 – 31 May 1410), also called the Elder and the Ecclesiastic, was King of Aragon, Valencia, Sardinia and Corsica and Count of Barcelona from 1396 and King of Sicily from 1409 (as Martin II). *(gold support)*
- `s01` He failed to secure the accession of his illegitimate grandson, Frederic, Count of Luna, and with him the rule of the House of Barcelona came to an end. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Jaulín - sub-question: Jaulín >> located in the administrative territorial entity -> sub-answer: Aragon; depends on steps []
2. Martin of Aragon - sub-question: Martin of #1 >> place of death -> sub-answer: Barcelona; depends on steps [1]
3. Gothic architecture - sub-question: When was the Palau de la Generalitat in #2 constructed? -> sub-answer: built in the 15th century; depends on steps [2]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Aragon' exact]  `s00` "Martin the Humane (29 July 1356 – 31 May 1410), also called the Elder and the Ecclesiastic, was King of Aragon, Valencia, Sardinia and Corsica and Count of Barcelona from 1396 and King of Sicily from 1409 (as Martin II)."  DEPENDS_ON  `s00` "Jaulín is a municipality located in the province of Zaragoza, Aragon, Spain."
- `e1` [B_derived_exact_anchor, anchor 'Barcelona' exact]  `s02` "Partial survivals of former royal residences include the Doge's Palace of Venice, the Palau de la Generalitat in Barcelona, built in the 15th century for the kings of Aragon, or the famous Conciergerie, former palace of the kings of France, in Paris."  DEPENDS_ON  `s00` "Martin the Humane (29 July 1356 – 31 May 1410), also called the Elder and the Ecclesiastic, was King of Aragon, Valencia, Sardinia and Corsica and Count of Barcelona from 1396 and King of Sicily from 1409 (as Martin II)."

---

## musique/3hop1__53690_161697_49779  (musique, 3hop1, hops=3)

**Question:** Who was a host of Who Wants to be a Millionaire who shares the same nationality as the author of The Feminine Mystique?  
**Gold answer(s):** Chris Harrison

**Passage `musique/3hop1__53690_161697_49779/p00` - Betty Friedan**
- `s00` Betty Friedan ( February 4, 1921 – February 4, 2006) was an American feminist writer and activist. *(gold support)*
- `s01` A leading figure in the women's movement in the United States, her 1963 book The Feminine Mystique is often credited with sparking the second wave of American feminism in the 20th century. *(gold support)*
- `s02` In 1966, Friedan co-founded and was elected the first president of the National Organization for Women (NOW), which aimed to bring women "into the mainstream of American society now [in] fully equal partnership with men." *(gold support)*

**Passage `musique/3hop1__53690_161697_49779/p01` - Who Wants to Be a Millionaire (American game show)**
- `s00` The original U.S. version aired on ABC from August 16, 1999 to June 27, 2002, and was hosted by Regis Philbin. *(gold support)*
- `s01` The daily syndicated version of the show began airing on September 16, 2002, and was hosted for eleven seasons by Meredith Vieira until May 31, 2013. *(gold support)*
- `s02` Later hosts included Cedric the Entertainer in the 2013 -- 14 season, Terry Crews in the following season (2014 -- 15), and Chris Harrison, who began hosting on September 14, 2015. *(gold support)*

**Passage `musique/3hop1__53690_161697_49779/p06` - The Feminine Mystique**
- `s00` The Feminine Mystique is a book written by Betty Friedan which is widely credited with sparking the beginning of second - wave feminism in the United States. *(gold support)*
- `s01` It was published on February 19, 1963 by W.W. *(gold support)*
- `s02` Norton. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. The Feminine Mystique - sub-question: who wrote the 1963 book the feminine mystique quizlet -> sub-answer: Betty Friedan; depends on steps []
2. Betty Friedan - sub-question: What nationality was #1 ? -> sub-answer: American; depends on steps [1]
3. Who Wants to Be a Millionaire (American game show) - sub-question: #2 who wants to be a millionaire host -> sub-answer: Chris Harrison; depends on steps [2]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Betty Friedan' exact]  `s00` "Betty Friedan ( February 4, 1921 – February 4, 2006) was an American feminist writer and activist."  DEPENDS_ON  `s00` "The Feminine Mystique is a book written by Betty Friedan which is widely credited with sparking the beginning of second - wave feminism in the United States."
- `e1` [C_derived_fallback_anchor, anchor 'American' fallback]  `s00` "The original U.S. version aired on ABC from August 16, 1999 to June 27, 2002, and was hosted by Regis Philbin."  DEPENDS_ON  `s00` "Betty Friedan ( February 4, 1921 – February 4, 2006) was an American feminist writer and activist."

---

## musique/4hop2__567956_14670_8987_8974  (musique, 4hop2, hops=4)

**Question:** A country's military branch, which in the US contains the Air Defense Artillery, was unprepared for the invasion of the country that experienced a normalization period. The unprepared country was the only communist country to have an embassy where?  
**Gold answer(s):** Alfredo Stroessner's Paraguay | Alfredo Stroessner

**Passage `musique/4hop2__567956_14670_8987_8974/p08` - Josip Broz Tito**
- `s00` In 1968, Tito offered Czechoslovak leader Alexander Dubček to fly to Prague on three hours notice if Dubček needed help in facing down the Soviets. *(gold support)*
- `s01` In April 1969, Tito removed generals Ivan Gošnjak and Rade Hamović in the aftermath of the invasion of Czechoslovakia due to the unpreparedness of the Yugoslav army to respond to a similar invasion of Yugoslavia. *(gold support)*

**Passage `musique/4hop2__567956_14670_8987_8974/p11` - United States Army**
- `s00` Currently, the army is divided into the Regular Army, the Army Reserve, and the Army National Guard. *(gold support)*
- `s01` The army is also divided into major branches such as Air Defense Artillery, Infantry, Aviation, Signal Corps, Corps of Engineers, and Armor. *(gold support)*
- `s02` Before 1903 members of the National Guard were considered state soldiers unless federalized (i.e., activated) by the President. *(gold support)*
- `s03` Since the Militia Act of 1903 all National Guard soldiers have held dual status: as National Guardsmen under the authority of the governor of their state or territory and, when activated, as a reserve of the U.S. Army under the authority of the President. *(gold support)*

**Passage `musique/4hop2__567956_14670_8987_8974/p17` - Prague underground (culture)**
- `s00` Prague underground was an underground culture developed in Prague, Czechoslovakia in the late 1960s and 1970s during the Normalization period. *(gold support)*
- `s01` The movement was characterized by resistance against conformity, conventions, and consumerism. *(gold support)*
- `s02` Because of its non-conformity, it had serious problems with the communist regime which considered it as a political opposition. *(gold support)*

**Passage `musique/4hop2__567956_14670_8987_8974/p19` - Josip Broz Tito**
- `s00` Because of its neutrality, Yugoslavia would often be rare among Communist countries to have diplomatic relations with right-wing, anti-Communist governments. *(gold support)*
- `s01` For example, Yugoslavia was the only communist country allowed to have an embassy in Alfredo Stroessner's Paraguay. *(gold support)*
- `s02` One notable exception to Yugoslavia's neutral stance toward anti-communist countries was Chile under Pinochet; Yugoslavia was one of many countries which severed diplomatic relations with Chile after Salvador Allende was overthrown. *(gold support)*
- `s03` Yugoslavia also provided military aid and arms supplies to staunchly anti-Communist regimes such as that of Guatemala under Kjell Eugenio Laugerud García. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Prague underground (culture) - sub-question: Normalization >> country -> sub-answer: Czechoslovakia; depends on steps []
2. United States Army - sub-question: The Air Defense Artillery is a branch of what? -> sub-answer: the Army; depends on steps []
3. Josip Broz Tito - sub-question: What #2 was unprepared for the invasion of #1 ? -> sub-answer: Yugoslavia; depends on steps [1, 2]
4. Josip Broz Tito - sub-question: #3 was the only communist country to have an embassy where? -> sub-answer: Alfredo Stroessner's Paraguay; depends on steps [3]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Czechoslovakia' exact]  `s01` "In April 1969, Tito removed generals Ivan Gošnjak and Rade Hamović in the aftermath of the invasion of Czechoslovakia due to the unpreparedness of the Yugoslav army to respond to a similar invasion of Yugoslavia."  DEPENDS_ON  `s00` "Prague underground was an underground culture developed in Prague, Czechoslovakia in the late 1960s and 1970s during the Normalization period."
- `e1` [B_derived_exact_anchor, anchor 'the Army' exact]  `s01` "In April 1969, Tito removed generals Ivan Gošnjak and Rade Hamović in the aftermath of the invasion of Czechoslovakia due to the unpreparedness of the Yugoslav army to respond to a similar invasion of Yugoslavia."  DEPENDS_ON  `s00` "Currently, the army is divided into the Regular Army, the Army Reserve, and the Army National Guard."
- `e2` [B_derived_exact_anchor, anchor 'Yugoslavia' exact]  `s00` "Because of its neutrality, Yugoslavia would often be rare among Communist countries to have diplomatic relations with right-wing, anti-Communist governments."  DEPENDS_ON  `s01` "In April 1969, Tito removed generals Ivan Gošnjak and Rade Hamović in the aftermath of the invasion of Czechoslovakia due to the unpreparedness of the Yugoslav army to respond to a similar invasion of Yugoslavia."

---

## musique/4hop1__777217_32392_823060_610794  (musique, 4hop1, hops=4)

**Question:** What county is the city that shares a border with the state capital of the state where Andrew Deveaux was born located in?  
**Gold answer(s):** Richland County | Richland County, South Carolina

**Passage `musique/4hop1__777217_32392_823060_610794/p01` - Forest Acres, South Carolina**
- `s00` Forest Acres is a city in Richland County, South Carolina, United States. *(gold support)*
- `s01` The population was 10,361 at the 2010 census. *(gold support)*
- `s02` It is part of the Columbia, South Carolina, Metropolitan Statistical Area. *(gold support)*

**Passage `musique/4hop1__777217_32392_823060_610794/p05` - Charleston, South Carolina**
- `s00` Although the city lost the status of state capital to Columbia in 1786, Charleston became even more prosperous in the plantation-dominated economy of the post-Revolutionary years. *(gold support)*
- `s01` The invention of the cotton gin in 1793 revolutionized the processing of this crop, making short-staple cotton profitable. *(gold support)*
- `s02` It was more easily grown in the upland areas, and cotton quickly became South Carolina's major export commodity. *(gold support)*
- `s03` The Piedmont region was developed into cotton plantations, to which the sea islands and Lowcountry were already devoted. *(gold support)*
- `s04` Slaves were also the primary labor force within the city, working as domestics, artisans, market workers, and laborers. *(gold support)*

**Passage `musique/4hop1__777217_32392_823060_610794/p12` - Andrew Deveaux**
- `s00` Andrew Deveaux (30 April 1758 – 11 July 1812) was an American Loyalist from South Carolina who is most famous for his recapture of the Bahamas in 1783. *(gold support)*

**Passage `musique/4hop1__777217_32392_823060_610794/p18` - WWNQ**
- `s00` WWNQ is a radio station licensed to Forest Acres, South Carolina, serving the Columbia, South Carolina market. *(gold support)*
- `s01` Owned by Midlands Media Group LLC, the station broadcasts a country music format branded as 94.3 The Dude. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Andrew Deveaux - sub-question: Andrew Deveaux >> place of birth -> sub-answer: South Carolina; depends on steps []
2. Charleston, South Carolina - sub-question: What city became the state capital of #1 ? -> sub-answer: Columbia; depends on steps [1]
3. WWNQ - sub-question: #2 >> shares border with -> sub-answer: Forest Acres; depends on steps [2]
4. Forest Acres, South Carolina - sub-question: #3 >> located in the administrative territorial entity -> sub-answer: Richland County; depends on steps [3]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'South Carolina' fallback]  `s00` "Although the city lost the status of state capital to Columbia in 1786, Charleston became even more prosperous in the plantation-dominated economy of the post-Revolutionary years."  DEPENDS_ON  `s00` "Andrew Deveaux (30 April 1758 – 11 July 1812) was an American Loyalist from South Carolina who is most famous for his recapture of the Bahamas in 1783."
- `e1` [B_derived_exact_anchor, anchor 'Columbia' exact]  `s00` "WWNQ is a radio station licensed to Forest Acres, South Carolina, serving the Columbia, South Carolina market."  DEPENDS_ON  `s00` "Although the city lost the status of state capital to Columbia in 1786, Charleston became even more prosperous in the plantation-dominated economy of the post-Revolutionary years."
- `e2` [B_derived_exact_anchor, anchor 'Forest Acres' exact]  `s00` "Forest Acres is a city in Richland County, South Carolina, United States."  DEPENDS_ON  `s00` "WWNQ is a radio station licensed to Forest Acres, South Carolina, serving the Columbia, South Carolina market."

---

## musique/2hop__424294_19033  (musique, 2hop, hops=2)

**Question:** Where did the author of A Lion's Tale: Around the World in Spandex win in 2008?  
**Gold answer(s):** Great American Bash | The Great American Bash

**Passage `musique/2hop__424294_19033/p06` - Professional wrestling**
- `s00` A referee may stop the match when they or official ring physician decides that a wrestler cannot safely continue the match. *(gold support)*
- `s01` This may be decided if the wrestler cannot continue the match due to an injury. *(gold support)*
- `s02` At the Great American Bash in 2008, Chris Jericho was declared the winner of a match against Shawn Michaels when Michaels could not defend himself due to excessive blood loss and impaired vision. *(gold support)*
- `s03` At NXT TakeOver: Rival in 2015, the referee stopped the match when Sami Zayn could not defend himself due to an injury sustained against Kevin Owens for the NXT Championship. *(gold support)*

**Passage `musique/2hop__424294_19033/p17` - A Lion's Tale**
- `s00` A Lion's Tale: Around the World in Spandex is an autobiography of professional wrestler, Chris Jericho. *(gold support)*
- `s01` It details his life from his early years, to his début for World Wrestling Entertainment (WWE), on August 9, 1999. *(gold support)*
- `s02` The book is followed by a sequel, "", which was released in 2011. *(gold support)*
- `s03` A second sequel, "Best in the World (At What I Have No Idea)", was released in 2014. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. A Lion's Tale - sub-question: A Lion's Tale: Around the World in Spandex >> author -> sub-answer: Chris Jericho; depends on steps []
2. Professional wrestling - sub-question: Where did #1 win in 2008? -> sub-answer: Great American Bash; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Chris Jericho' exact]  `s02` "At the Great American Bash in 2008, Chris Jericho was declared the winner of a match against Shawn Michaels when Michaels could not defend himself due to excessive blood loss and impaired vision."  DEPENDS_ON  `s00` "A Lion's Tale: Around the World in Spandex is an autobiography of professional wrestler, Chris Jericho."

---

## musique/2hop__6956_192417  (musique, 2hop, hops=2)

**Question:** The league the New England Patriots belongs to is an example of what?  
**Gold answer(s):** sports league | Sports league | league

**Passage `musique/2hop__6956_192417/p06` - Boston**
- `s00` While they have played in suburban Foxborough since 1971, the New England Patriots of the National Football League were founded in 1960 as the Boston Patriots, changing their name after relocating. *(gold support)*
- `s01` The team won the Super Bowl after the 2001, 2003, 2004, and 2014 seasons. *(gold support)*
- `s02` They share Gillette Stadium with the New England Revolution of Major League Soccer. *(gold support)*
- `s03` The Boston Breakers of Women's Professional Soccer, which formed in 2009, play their home games at Dilboy Stadium in Somerville. *(gold support)*

**Passage `musique/2hop__6956_192417/p15` - Sports league ranking**
- `s00` In a sports league, the ranking of a team is the place where it is within the division. *(gold support)*
- `s01` Generally, ranking is based on won-lost record of games, with the team with the best record at the top, and the worst record at the bottom. *(gold support)*
- `s02` Another common method is a points-based ranking system, where a team is awarded a certain number of points per win, fewer points per tie, and none for a loss. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Boston - sub-question: What league do the new England patriots belong to? -> sub-answer: the National Football League; depends on steps []
2. Sports league ranking - sub-question: #1 >> instance of -> sub-answer: sports league; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'the National Football League' fallback]  `s00` "In a sports league, the ranking of a team is the place where it is within the division."  DEPENDS_ON  `s00` "While they have played in suburban Foxborough since 1971, the New England Patriots of the National Football League were founded in 1960 as the Boston Patriots, changing their name after relocating."

---

## 2wikimultihopqa/bbefa25e08cc11ebbd93ac1f6bf848b6  (2wikimultihopqa, bridge_comparison, hops=4)

**Question:** Which film has the director who is older, Thought Moments or Roads Of Kiarostami?  
**Gold answer(s):** Roads Of Kiarostami

**Passage `2wikimultihopqa/bbefa25e08cc11ebbd93ac1f6bf848b6/p00` - Thought Moments**
- `s00` Thought Moments( 2004) is an anthropological short film in the style of cinéma vérité by Michael Simon Toon. *(gold support)*
- `s01` Toon, a former Buddhist monk, titled" Thought Moments" after the Buddhist term for the mental states we experience when a physical or mental object enters the mind.
- `s02` The film is used in the study of microexpressions, eye accessing cues, and the universality of facial expressions.
- `s03` Toon( off camera) interviews a diverse sample of individuals in public places across the United Kingdom asking a set of ten simple but emotionally evocative questions.
- `s04` The film uses variable frame rates to highlight distinct emotions, as well as their sequence and timing, that each individual expresses within seconds or fractions of a second after being asked questions, such as" What do you love most?
- `s05` Are you happy or sad?" and" What are you afraid of?"
- `s06` Consistency of composition, lighting, and contrast facilitates the analysis of both the differences and similarities of the interviewees' facial expressions.
- `s07` Toon also released a version of the film with superimposed theoretical eye accessing cue chart.
- `s08` Both versions are studied and reproduced by students of psychology in several languages.

**Passage `2wikimultihopqa/bbefa25e08cc11ebbd93ac1f6bf848b6/p02` - Roads of Kiarostami**
- `s00` Roads of Kiarostami is a 2005 Iranian documentary film directed by Abbas Kiarostami. *(gold support)*
- `s01` Looking to his own art for inspiration, Abbas Kiarostami reflects on the power of landscape, which combines views of the Iranian auteur's austere black- and- white photographs with poetic observations, engaging music and a politically provocative finale.

**Passage `2wikimultihopqa/bbefa25e08cc11ebbd93ac1f6bf848b6/p03` - Abbas Kiarostami**
- `s00` Abbas Kiarostami( 22 June 1940 – 4 July 2016) was an Iranian film director, screenwriter, poet, photographer, and film producer. *(gold support)*
- `s01` An active film- maker from 1970, Kiarostami had been involved in the production of over forty films, including shorts and documentaries.
- `s02` Kiarostami attained critical acclaim for directing the" Koker" trilogy( 1987– 1994)," Close- Up"( 1990)," The Wind Will Carry Us"( 1999), and" Taste of Cherry"( 1997), which was awarded the Palme d' Or at the Cannes Film Festival that year.
- `s03` In later works," Certified Copy"( 2010) and" Like Someone in Love"( 2012), he filmed for the first time outside Iran: in Italy and Japan, respectively.
- `s04` His films" Where Is the Friend ’s Home? Close- Up", and" The Wind Will Carry Us" were ranked among the 100 best foreign films in a 2018 critics' poll by BBC Culture.
- `s05` " Close- Up" was also ranked one of the 50 greatest movies of all time in the famous decennial" Sight& Sound" poll conducted in 2012.
- `s06` Kiarostami had worked extensively as a screenwriter, film editor, art director and producer and had designed credit titles and publicity material.
- `s07` He was also a poet, photographer, painter, illustrator, and graphic designer.
- `s08` He was part of a generation of filmmakers in the Iranian New Wave, a Persian cinema movement that started in the late 1960s and includes pioneering directors such as Bahram Beyzai, Nasser Taghvai, Ali Hatami, Masoud Kimiai, Dariush Mehrjui, Sohrab Shahid- Saless and Parviz Kimiavi.
- `s09` These filmmakers share many common techniques including the use of poetic dialogue and allegorical storytelling dealing with political and philosophical issues.
- `s10` Kiarostami had a reputation for using child protagonists, for documentary- style narrative films, for stories that take place in rural villages, and for conversations that unfold inside cars, using stationary mounted cameras.
- `s11` He is also known for his use of Persian poetry in the dialogue, titles, and themes of his films.
- `s12` Kiarostami's films contain a notable degree of ambiguity, an unusual mixture of simplicity and complexity, and often a mix of fictional and documentary elements.
- `s13` The concepts of change and continuity, in addition to the themes of life and death, play a major role in Kiarostami's works.

**Passage `2wikimultihopqa/bbefa25e08cc11ebbd93ac1f6bf848b6/p08` - Michael Simon Toon**
- `s00` Michael Simon Toon( born 12 March 1977) is an English photographer, filmmaker, designer and builder. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Thought Moments -> sub-answer: Michael Simon Toon; depends on steps []
2. Roads of Kiarostami -> sub-answer: Abbas Kiarostami; depends on steps []
3. Michael Simon Toon -> sub-answer: 12 March 1977; depends on steps [1]
4. Abbas Kiarostami -> sub-answer: 22 June 1940; depends on steps [2]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Michael Simon Toon' exact]  `s00` "Michael Simon Toon( born 12 March 1977) is an English photographer, filmmaker, designer and builder."  DEPENDS_ON  `s00` "Thought Moments( 2004) is an anthropological short film in the style of cinéma vérité by Michael Simon Toon."
- `e1` [B_derived_exact_anchor, anchor 'Abbas Kiarostami' exact]  `s00` "Abbas Kiarostami( 22 June 1940 – 4 July 2016) was an Iranian film director, screenwriter, poet, photographer, and film producer."  DEPENDS_ON  `s00` "Roads of Kiarostami is a 2005 Iranian documentary film directed by Abbas Kiarostami."

---

## 2wikimultihopqa/ca3e5ea408cc11ebbd93ac1f6bf848b6  (2wikimultihopqa, bridge_comparison, hops=4)

**Question:** Which film has the director born later, Freakin' Beautiful World or Billy Two Hats?  
**Gold answer(s):** Freakin' Beautiful World

**Passage `2wikimultihopqa/ca3e5ea408cc11ebbd93ac1f6bf848b6/p04` - Ted Kotcheff**
- `s00` William Theodore Kotcheff( born April 7, 1931) is a Bulgarian- Canadian film and television director and producer, known primarily for his work on British and American television productions such as" Armchair Theatre" and. *(gold support)*
- `s01` He has also directed numerous successful films including the Australian" Wake in Fright"( 1971), action films such as the original" Rambo" movie" First Blood"( 1982) and" Uncommon Valor"( 1983), and comedies like" Weekend at Bernie's"( 1989)," Fun with Dick and Jane"( 1977), and" North Dallas Forty"( 1979).
- `s02` He is sometimes credited as William T. Kotcheff, and resides in Beverly Hills, California.
- `s03` Given his ancestry, Kotcheff has Bulgarian citizenship.

**Passage `2wikimultihopqa/ca3e5ea408cc11ebbd93ac1f6bf848b6/p06` - Jarmo Lampela**
- `s00` Jarmo Lampela( born 9 October 1964) is a Finnish film director and screenwriter. *(gold support)*
- `s01` He has directed more than 15 films since 1988.
- `s02` His 2003 film" Eila" was entered into the 25th Moscow International Film Festival.
- `s03` In 2013 he is scheduled to direct a new film" Weather".

**Passage `2wikimultihopqa/ca3e5ea408cc11ebbd93ac1f6bf848b6/p08` - Freakin' Beautiful World**
- `s00` Freakin' Beautiful World is a 1997 Finnish drama film written and directed by Jarmo Lampela. *(gold support)*
- `s01` The film is about two teenage boys from Helsinki who owe money to a local drug dealer.
- `s02` In order to pay their debt, they have to travel to Stockholm to collect drugs for the drug dealer.
- `s03` The film won Jussi Awards for Best Film, Best Cinematography, and Best Editing.

**Passage `2wikimultihopqa/ca3e5ea408cc11ebbd93ac1f6bf848b6/p09` - Billy Two Hats**
- `s00` Billy Two Hats is a 1974 Western film directed by Ted Kotcheff. *(gold support)*
- `s01` It stars Gregory Peck, Jack Warden and Desi Arnaz, Jr. Filmed on- location in Israel," Billy Two Hats" is from a script by Scottish writer Alan Sharp, the screenwriter of" Rob Roy" and" Ulzana's Raid".

**Proposed reasoning steps (dataset order):**
1. Freakin' Beautiful World -> sub-answer: Jarmo Lampela; depends on steps []
2. Billy Two Hats -> sub-answer: Ted Kotcheff; depends on steps []
3. Jarmo Lampela -> sub-answer: 9 October 1964; depends on steps [1]
4. Ted Kotcheff -> sub-answer: April 7, 1931; depends on steps [2]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Jarmo Lampela' exact]  `s00` "Jarmo Lampela( born 9 October 1964) is a Finnish film director and screenwriter."  DEPENDS_ON  `s00` "Freakin' Beautiful World is a 1997 Finnish drama film written and directed by Jarmo Lampela."
- `e1` [C_derived_fallback_anchor, anchor 'Ted Kotcheff' fallback]  `s00` "William Theodore Kotcheff( born April 7, 1931) is a Bulgarian- Canadian film and television director and producer, known primarily for his work on British and American television productions such as" Armchair Theatre" and."  DEPENDS_ON  `s00` "Billy Two Hats is a 1974 Western film directed by Ted Kotcheff."

---

## 2wikimultihopqa/1806efe409b911ebbdb0ac1f6bf848b6  (2wikimultihopqa, comparison, hops=2)

**Question:** Are both mountains, Pizzo Della Croce and Geierwand, located in the same country?  
**Gold answer(s):** yes

**Passage `2wikimultihopqa/1806efe409b911ebbdb0ac1f6bf848b6/p01` - Geierwand**
- `s00` The Geierwand is a mountain in the Dolomites in South Tyrol, Italy. *(gold support)*

**Passage `2wikimultihopqa/1806efe409b911ebbdb0ac1f6bf848b6/p02` - Pizzo della Croce**
- `s00` Pizzo della Croce is a mountain of Lombardy, Italy. *(gold support)*
- `s01` It has an elevation of 1,491 metres.

**Proposed reasoning steps (dataset order):**
1. Pizzo della Croce -> sub-answer: Italy; depends on steps []
2. Geierwand -> sub-answer: Italy; depends on steps []

**Proposed dependency edges:**
- (none proposed)

---

## 2wikimultihopqa/cfad61500bdd11eba7f7acde48001122  (2wikimultihopqa, compositional, hops=2)

**Question:** Where did the composer of film Bad Man'S River die?  
**Gold answer(s):** Madrid

**Passage `2wikimultihopqa/cfad61500bdd11eba7f7acde48001122/p02` - Bad Man's River**
- `s00` Bad Man's River (and) is a 1971 European comedy Spaghetti western directed by Eugenio Martín and starring Lee Van Cleef, James Mason, Gina Lollobrigida and Simón Andreu.
- `s01` Soundtrack was composed by Tony Duhig, Peter Jonfield, Glyn Havard and Waldo de los Ríos. *(gold support)*

**Passage `2wikimultihopqa/cfad61500bdd11eba7f7acde48001122/p03` - Waldo de los Ríos**
- `s00` Osvaldo Nicolás Ferraro de los Ríos (7 September 1934 – 28 March 1977) better known as Waldo de los Ríos was an Argentine composer, conductor and arranger.
- `s01` De los Ríos was born in Buenos Aires into a musical family; his father was a musician and his mother a well known folk singer; he studied composition and arranging at the National Conservatory of Music under Alberto Ginastera and Teodoro Fuchs.
- `s02` He was inspired by an eclectic range of music and formed a musical group called "The Waldos" which crossed folk music with electronic sounds.
- `s03` De los Ríos turned to work in cinema and film sound tracks where his compositions were heard in the 1967 film "Savage Pampas", for which he received a prestigious award from the Argentine Academy of Cinematography Arts and Sciences.
- `s04` He relocated to the USA in 1958 and then to Spain in 1962.
- `s05` He is best remembered for his ability to transform European classical music into pop music.
- `s06` His 1971 arrangement of Mozart's "Symphony No. 40", recorded with the Manuel de Falla orchestra, reached the top spot in the Dutch charts and scored a top 10 hit in several other European countries.
- `s07` In 1970, prior to this success, Waldo de los Ríos had already climbed the charts around Europe and America with Ludwig van Beethoven's "Ode To Joy", which he arranged and conducted for Miguel Ríos.
- `s08` His record "Mozart in the Seventies" rearranged famous Mozart pieces in a contemporary style, with a large percussion section.
- `s09` Several tracks from it were used as theme tunes to BBC programmes of that era, including the theme to the BBC's coverage of the "Horse of the Year Show" (his reworking of Mozart's "A Musical Joke").
- `s10` His re-working of "Eine Kleine Nachtmusik", used for many years as the theme to the Radio 4 quiz show "Brain of Britain", was the subject of frequent complaints from classical music fans (with whom the show was popular) and presenter Robert Robinson described it on air as "Mozart plus sacrilege".
- `s11` He also issued an album "Symphonies for the Seventies" which included Mozart's Symphony no. 40 and other major composers including Dvořák's "New World".
- `s12` He arranged and conducted the Spanish entry for the Eurovision Song Contest 1971, "En un mundo nuevo" for Karina.
- `s13` The song landed a respectable second position and hit the charts in several European countries.
- `s14` He was married to actress turned journalist/
- `s15` author Isabel Pisano (born in Montevideo, Uruguay, 1944).
- `s16` Pisano later documented part of his life in her autobiography "El Amado Fantasma"
- `s17` (Plaza y Janés, 2002).
- `s18` A victim of an acute depression while working on "Don Juan Tenorio", De los Ríos committed suicide in Madrid in 1977. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Bad Man's River -> sub-answer: Waldo de los Ríos; depends on steps []
2. Waldo de los Ríos -> sub-answer: Madrid; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Waldo de los Ríos' exact]  `s00` "Osvaldo Nicolás Ferraro de los Ríos (7 September 1934 – 28 March 1977) better known as Waldo de los Ríos was an Argentine composer, conductor and arranger."  DEPENDS_ON  `s01` "Soundtrack was composed by Tony Duhig, Peter Jonfield, Glyn Havard and Waldo de los Ríos."

---

## 2wikimultihopqa/bf39cea20bd911eba7f7acde48001122  (2wikimultihopqa, compositional, hops=2)

**Question:** Which country the director of film E A Vida Continua... is from?  
**Gold answer(s):** Angolan

**Passage `2wikimultihopqa/bf39cea20bd911eba7f7acde48001122/p05` - Paulo Figueiredo**
- `s00` Paulo José Lopes de Figueiredo (born 28 November 1972) is an Angolan retired footballer who played as a central midfielder. *(gold support)*
- `s01` He spent the bulk of his 17-year professional career with Santa Clara, amassing Primeira Liga totals of 97 matches and eight goals during three seasons (eight in total with the club).
- `s02` An Angolan international for five years
- `s03` , Figueiredo earned 38 caps and represented the nation at the 2006 World Cup and two Africa Cup of Nations tournaments.

**Passage `2wikimultihopqa/bf39cea20bd911eba7f7acde48001122/p08` - E a Vida Continua...**
- `s00` E a Vida Continua
- `s01` ... is a 2012 Brazilian drama film directed by Paulo Figueiredo, based on the book of the same name by the medium Chico Xavier. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. E a Vida Continua... -> sub-answer: Paulo Figueiredo; depends on steps []
2. Paulo Figueiredo -> sub-answer: Angolan; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Paulo Figueiredo' fallback]  `s00` "Paulo José Lopes de Figueiredo (born 28 November 1972) is an Angolan retired footballer who played as a central midfielder."  DEPENDS_ON  `s01` "... is a 2012 Brazilian drama film directed by Paulo Figueiredo, based on the book of the same name by the medium Chico Xavier."

---

## 2wikimultihopqa/a9f090fa0baf11ebab90acde48001122  (2wikimultihopqa, inference, hops=2)

**Question:** Who is Richard De Montfort's paternal grandfather?  
**Gold answer(s):** Amaury I de Montfort

**Passage `2wikimultihopqa/a9f090fa0baf11ebab90acde48001122/p03` - Simon I de Montfort**
- `s00` Simon I de Montfort (c. 1025 – 25 September 1087) was a French nobleman.
- `s01` He was born in Montfort l'Amaury, in the Duchy of Normandy, and became its lord.
- `s02` He was the son of Amaury I de Montfort and Bertrade. *(gold support)*
- `s03` At his death he was buried about away in Epernon, because it was the site of the fortress he was instrumental in constructing.

**Passage `2wikimultihopqa/a9f090fa0baf11ebab90acde48001122/p06` - Richard de Montfort**
- `s00` Richard de Montfort (Montfort l'Amaury, Ile de France, France – 1092), was the son of Simon I de Montfort, Count of Évreux (c. 1025–1087) and Agnès d'Évreux (c. 1030 – c. 1087), daughter of Richard, Count of Évreux. *(gold support)*
- `s01` He succeeded his half brother Amaury II in 1089 as lord of Montfort-l'Amaury.
- `s02` In November 1092, he was killed in battle.
- `s03` Orderic Vitalis records that he succeeded his half-brother in 1089 and "was relentless in his attempts to take vengeance on William of Breteuil for Amaury's fate".
- `s04` He was mortally wounded in an attack on Conches, during the war between Raoul III de Tosny and William, Count of Évreux triggered by the enmity between their wives.
- `s05` He died without an heir and left Montfort to his brother, Simon II.
- `s06` He was buried in Épernon, Eure-et-Loir, France.

**Proposed reasoning steps (dataset order):**
1. Richard de Montfort -> sub-answer: Simon I de Montfort; depends on steps []
2. Simon I de Montfort -> sub-answer: Amaury I de Montfort; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Simon I de Montfort' exact]  `s00` "Simon I de Montfort (c. 1025 – 25 September 1087) was a French nobleman."  DEPENDS_ON  `s00` "Richard de Montfort (Montfort l'Amaury, Ile de France, France – 1092), was the son of Simon I de Montfort, Count of Évreux (c. 1025–1087) and Agnès d'Évreux (c. 1030 – c. 1087), daughter of Richard, Count of Évreux."

---

## 2wikimultihopqa/efb76f1e0baf11ebab90acde48001122  (2wikimultihopqa, inference, hops=2)

**Question:** Who is Ahmose-Nefertari's maternal grandfather?  
**Gold answer(s):** Senakhtenre Ahmose

**Passage `2wikimultihopqa/efb76f1e0baf11ebab90acde48001122/p03` - Ahhotep I**
- `s00` Ahhotep
- `s01` I (alternatively Anglicized "Ahhotpe" or "AahhotepIah (the Moon) is satisfied") was an Ancient Egyptian queen who lived
- `s02` circa 1560–1530 BC, during the end of the Seventeenth Dynasty of Egypt.
- `s03` She was the daughter of Queen Tetisheri (known as Teti the Small) and Senakhtenre Ahmose, and was probably the sister, as well as the queen consort, of Pharaoh Seqenenre Tao *(gold support)*
- `s04` ll.
- `s05` Ahhotep
- `s06` I had a long and influential life.
- `s07` She ruled as regent for her son Ahmose I for a time.
- `s08` Her titles include Great Royal Wife and "Associate of the White Crown Bearer" .
- `s09` The title "King's Mother"  was found on the Deir el-Bahari coffin.

**Passage `2wikimultihopqa/efb76f1e0baf11ebab90acde48001122/p08` - Ahmose-Nefertari**
- `s00` Ahmose-Nefertari of Ancient Egypt was the first queen of the 18th Dynasty.
- `s01` She was a daughter of Seqenenre Tao and Ahhotep I, and royal sister and the great royal wife of *(gold support)*
- `s02` Ahmose I. She was the mother of king Amenhotep I and may have served as his regent when he was young.
- `s03` Ahmose-Nefertari was deified after her death.

**Proposed reasoning steps (dataset order):**
1. Ahmose-Nefertari -> sub-answer: Ahhotep I; depends on steps []
2. Ahhotep I -> sub-answer: Senakhtenre Ahmose; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Ahhotep I' fallback]  `s03` "She was the daughter of Queen Tetisheri (known as Teti the Small) and Senakhtenre Ahmose, and was probably the sister, as well as the queen consort, of Pharaoh Seqenenre Tao"  DEPENDS_ON  `s01` "She was a daughter of Seqenenre Tao and Ahhotep I, and royal sister and the great royal wife of"

---

## 2wikimultihopqa/c818d9480baf11ebab90acde48001122  (2wikimultihopqa, inference, hops=2)

**Question:** Who is Frederick Of Luxembourg's paternal grandfather?  
**Gold answer(s):** Wigeric of Lotharingia

**Passage `2wikimultihopqa/c818d9480baf11ebab90acde48001122/p01` - Frederick of Luxembourg**
- `s00` Frederick of Luxembourg (965 – 6 October 1019), Count of Moselgau, was a son of Siegfried of Luxembourg and Hedwig of Nordgau. *(gold support)*
- `s01` By a wife whose name is unknown (certain historians give her as Ermentrude, Countess of Gleiberg), he had:

**Passage `2wikimultihopqa/c818d9480baf11ebab90acde48001122/p04` - Sigfried, Count of the Ardennes**
- `s00` Sigfried (or Siegfried) (– 28 October 998) was count of the Ardennes and the first person to rule Luxembourg.
- `s01` He was an advocate of the abbeys of St. Maximin in Trier and Saint Willibrord in Echternach.
- `s02` He may have been the son of Count Palatine Wigeric of Lotharingia and Cunigunda. *(gold support)*
- `s03` He was the founder of the House of Luxembourg, a branch of the House of Ardennes.

**Proposed reasoning steps (dataset order):**
1. Frederick of Luxembourg -> sub-answer: Siegfried of Luxembourg; depends on steps []
2. Sigfried, Count of the Ardennes -> sub-answer: Wigeric of Lotharingia; depends on steps []

**Proposed dependency edges:**
- (none proposed)

---

## 2wikimultihopqa/a635f66e088d11ebbd70ac1f6bf848b6  (2wikimultihopqa, bridge_comparison, hops=4)

**Question:** Which film has the director who is older than the other, Life As It Comes or Dear Wendy?   
**Gold answer(s):** Life As It Comes

**Passage `2wikimultihopqa/a635f66e088d11ebbd70ac1f6bf848b6/p01` - Stefano Incerti**
- `s00` Stefano Incerti( born 25 July 1965) is an Italian film director. *(gold support)*
- `s01` He has directed more than ten films since 1995.
- `s02` In 2014, Stefano directed the drama Snowscape, about Donato( Roberto De Francesco), a man looking for something that would secure his future, and Norah( Esther Elisha), a woman who abandoned and chased by a small- time gangster, from whom she may have stolen something big.

**Passage `2wikimultihopqa/a635f66e088d11ebbd70ac1f6bf848b6/p05` - Dear Wendy**
- `s00` Dear Wendy is a 2005 crime film directed by Thomas Vinterberg and written by Lars von Trier. *(gold support)*
- `s01` It stars Jamie Bell, Bill Pullman, Michael Angarano, Mark Webber, Danso Gordon, Novella Nelson and Alison Pill.
- `s02` It was an international co-production between Denmark, Germany, France, and the United Kingdom, filmed on- location in Copenhagen.
- `s03` The film had its world premiere at the 2005 Sundance Film Festival.
- `s04` It received an approval rating of 36% on Rotten Tomatoes based on 64 reviews and an average rating of 5.1 /10.
- `s05` Vinterberg won the Silver St. George for Best Director at the 27th Moscow International Film Festival.

**Passage `2wikimultihopqa/a635f66e088d11ebbd70ac1f6bf848b6/p06` - Thomas Vinterberg**
- `s00` Thomas Vinterberg( born 19 May 1969) is a Danish film director who, along with Lars von Trier, co-founded the Dogme 95 movement in filmmaking, which established rules for simplifying movie production. *(gold support)*
- `s01` He is best known for the films" The Celebration"( 1998)," Submarino"( 2010)," The Hunt"( 2012) and" Far from the Madding Crowd"( 2015).

**Passage `2wikimultihopqa/a635f66e088d11ebbd70ac1f6bf848b6/p07` - Life as It Comes**
- `s00` Life as It Comes is a 2003 Italian drama film directed by Stefano Incerti. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Life as It Comes -> sub-answer: Stefano Incerti; depends on steps []
2. Dear Wendy -> sub-answer: Thomas Vinterberg; depends on steps []
3. Stefano Incerti -> sub-answer: 25 July 1965; depends on steps [1]
4. Thomas Vinterberg -> sub-answer: 19 May 1969; depends on steps [2]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Stefano Incerti' exact]  `s00` "Stefano Incerti( born 25 July 1965) is an Italian film director."  DEPENDS_ON  `s00` "Life as It Comes is a 2003 Italian drama film directed by Stefano Incerti."
- `e1` [B_derived_exact_anchor, anchor 'Thomas Vinterberg' exact]  `s00` "Thomas Vinterberg( born 19 May 1969) is a Danish film director who, along with Lars von Trier, co-founded the Dogme 95 movement in filmmaking, which established rules for simplifying movie production."  DEPENDS_ON  `s00` "Dear Wendy is a 2005 crime film directed by Thomas Vinterberg and written by Lars von Trier."

---

## 2wikimultihopqa/65f06f70088411ebbd6dac1f6bf848b6  (2wikimultihopqa, bridge_comparison, hops=4)

**Question:** Do both Pandora And The Flying Dutchman and Special Delivery (1927 Film) films have the directors from the same country?  
**Gold answer(s):** yes

**Passage `2wikimultihopqa/65f06f70088411ebbd6dac1f6bf848b6/p00` - Albert Lewin**
- `s00` Albert Lewin (September 23, 1894 – May 9, 1968) was an American film director, producer, and screenwriter. *(gold support)*
- `s01` He was born in Brooklyn, New York and raised in Newark, New Jersey.
- `s02` He earned a master's degree at Harvard and taught English at the University of Missouri.
- `s03` During World War I, he served in the military and was afterwards appointed assistant national director of the American Jewish Relief Committee.
- `s04` He later became a drama and film critic for the "Jewish Tribune" until the early 1920s, when he went to Hollywood to become a reader for Samuel Goldwyn.
- `s05` Later he worked as a script clerk for directors King Vidor and Victor Sjöström before becoming a screenwriter at MGM in 1924.
- `s06` Lewin was appointed head of the studio's script department and by the late 1920s was Irving Thalberg's personal assistant and closest associate.
- `s07` Nominally credited as an associate producer, he produced several of MGM's most important films of the 1930s.
- `s08` After Thalberg's death, he joined Paramount as a producer in 1937, where he remained until 1941.
- `s09` Notable producing credits during this period include "True Confession" (1937), "Spawn of the North" (1938), "Zaza" (1939) and "So Ends Our Night" (1941).
- `s10` In 1942, Lewin began to direct.
- `s11` He made six films, writing all of them and producing several himself.
- `s12` As a director and writer, he showed literary and cultural aspirations in the selection and treatment of his themes.
- `s13` In 1966, Lewin published a novel, "The Unaltered Cat".

**Passage `2wikimultihopqa/65f06f70088411ebbd6dac1f6bf848b6/p01` - Roscoe Arbuckle**
- `s00` Roscoe Conkling" Fatty" Arbuckle( March 24, 1887 – June 29, 1933) was an American silent film actor, comedian, director, and screenwriter. *(gold support)*
- `s01` He started at the Selig Polyscope Company and eventually moved to Keystone Studios, where he worked with Mabel Normand and Harold Lloyd.
- `s02` He mentored Charlie Chaplin and discovered Buster Keaton and Bob Hope.
- `s03` He was one of the most popular silent stars of the 1910s and one of the highest paid actors in Hollywood, signing a contract in 1920 with Paramount Pictures for$ 14,000( equivalent to approximately 175,000 in dollars).
- `s04` Arbuckle was the defendant in three widely publicized trials between November 1921 and April 1922 for the alleged rape and manslaughter of actress Virginia Rappe.
- `s05` Rappe had fallen ill at a party hosted by Arbuckle at the St. Francis Hotel in San Francisco in September 1921, and she died four days later.
- `s06` A friend of Rappe accused Arbuckle of raping and accidentally killing her.
- `s07` The first two trials resulted in hung juries, but Buster Keaton defended him in the third trial, which acquitted him, and the jury gave him a formal written statement of apology.
- `s08` Despite Arbuckle's acquittal, the scandal has mostly overshadowed his legacy as a pioneering comedian.
- `s09` His films were banned by motion picture industry censor Will Hays after the trial and he was publicly ostracized.
- `s10` Hays lifted the ban within a year, but Arbuckle only worked sparingly through the 1920s.
- `s11` Keaton made an agreement to give him 35 percent of his profit from Buster Keaton Comedies Co.
- `s12` He later worked as a film director under the pseudonym William Goodrich.
- `s13` He was finally able to return to acting, making short two- reel comedies in 1932 – 33 for Warner Bros.
- `s14` Arbuckle died in his sleep of a heart attack in 1933 at age 46, reportedly on the day that he signed a contract with Warner Brothers to make a feature film.

**Passage `2wikimultihopqa/65f06f70088411ebbd6dac1f6bf848b6/p07` - Pandora and the Flying Dutchman**
- `s00` Pandora and the Flying Dutchman is a 1951 British Technicolor drama film made by Romulus Films and released by Metro- Goldwyn- Mayer in the United States.
- `s01` The film was directed by Albert Lewin and produced by Lewin and Joe Kaufmann from his own screenplay, based on the legend of the" Flying Dutchman". *(gold support)*
- `s02` It was filmed mainly on the Costa Brava.
- `s03` The land record speed scenes were shot at Pendine Sands in Wales.
- `s04` The film starred Ava Gardner and James Mason, featuring Nigel Patrick, Sheila Sim, Harold Warrender, Mario Cabré and Marius Goring.
- `s05` The cinematographer was Jack Cardiff.
- `s06` Most of the movie was shot on location in Tossa de Mar, Catalonia, Spain, where a statue of Gardner has been erected on the hill overlooking the town's main beach.
- `s07` MGM delayed its release until Gardner's star- making performance in" Show Boat"( 1951) could be seen.
- `s08` The tactic worked, and this film solidified her status as a rising star.

**Passage `2wikimultihopqa/65f06f70088411ebbd6dac1f6bf848b6/p08` - Special Delivery (1927 film)**
- `s00` Special Delivery is a 1927 American silent comedy film directed by Roscoe Arbuckle( as William Goodrich), starring Eddie Cantor, written by Cantor, John F. Goodrich and George Marion Jr.( with Larry Semon, uncredited). *(gold support)*
- `s01` It was released by Paramount Pictures.

**Proposed reasoning steps (dataset order):**
1. Pandora and the Flying Dutchman -> sub-answer: Albert Lewin; depends on steps []
2. Special Delivery (1927 film) -> sub-answer: Roscoe Arbuckle; depends on steps []
3. Albert Lewin -> sub-answer: American; depends on steps [1]
4. Roscoe Arbuckle -> sub-answer: American; depends on steps [2]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Albert Lewin' exact]  `s00` "Albert Lewin (September 23, 1894 – May 9, 1968) was an American film director, producer, and screenwriter."  DEPENDS_ON  `s01` "The film was directed by Albert Lewin and produced by Lewin and Joe Kaufmann from his own screenplay, based on the legend of the" Flying Dutchman"."
- `e1` [C_derived_fallback_anchor, anchor 'Roscoe Arbuckle' fallback]  `s00` "Roscoe Conkling" Fatty" Arbuckle( March 24, 1887 – June 29, 1933) was an American silent film actor, comedian, director, and screenwriter."  DEPENDS_ON  `s00` "Special Delivery is a 1927 American silent comedy film directed by Roscoe Arbuckle( as William Goodrich), starring Eddie Cantor, written by Cantor, John F. Goodrich and George Marion Jr.( with Larry Semon, uncredited)."

---

## 2wikimultihopqa/33c77397088311ebbd6dac1f6bf848b6  (2wikimultihopqa, comparison, hops=2)

**Question:** Who lived longer, Mathias Rosenblad or Jiří Baumruk?  
**Gold answer(s):** Mathias Rosenblad

**Passage `2wikimultihopqa/33c77397088311ebbd6dac1f6bf848b6/p00` - Jiří Baumruk**
- `s00` Jiří Baumruk( 27 June 1930 – 23 November 1989) was a Czech professional basketball player. *(gold support)*

**Passage `2wikimultihopqa/33c77397088311ebbd6dac1f6bf848b6/p03` - Mathias Rosenblad**
- `s00` Count Mathias Rosenblad (June 23, 1758 – September 4, 1847) was a Swedish politician and government official. *(gold support)*
- `s01` In 1797, he was elected a member of the Royal Swedish Academy of Sciences.

**Proposed reasoning steps (dataset order):**
1. Mathias Rosenblad -> sub-answer: June 23, 1758; depends on steps []
2. Mathias Rosenblad -> sub-answer: September 4, 1847; depends on steps []
3. Jiří Baumruk -> sub-answer: 27 June 1930; depends on steps []
4. Jiří Baumruk -> sub-answer: 23 November 1989; depends on steps []

**Proposed dependency edges:**
- (none proposed)

---

## 2wikimultihopqa/40a0ab780bda11eba7f7acde48001122  (2wikimultihopqa, compositional, hops=2)

**Question:** When did Harald Iii Of Denmark's father die?  
**Gold answer(s):** 28 April 1076

**Passage `2wikimultihopqa/40a0ab780bda11eba7f7acde48001122/p00` - Harald III of Denmark**
- `s00` Harald III (Harald the Whetstone, ; – April 17, 1080) was King of Denmark from 1076 to 1080.
- `s01` Harald III was an illegitimate son of Danish king Sweyn II Estridsson, and contested the crown with some of his brothers. *(gold support)*
- `s02` He was a peaceful ruler who initiated a number of reforms.
- `s03` Harald was married to his cousin Margareta Hasbjörnsdatter, but did not leave any heirs, and was succeeded by his brother Canute IV the Saint.
- `s04` Four of his half-brothers were in turn crowned Danish kings, with his youngest brother becoming the Danish king known as Harald IV (Harald the Young), Danish: Harald Olpe.

**Passage `2wikimultihopqa/40a0ab780bda11eba7f7acde48001122/p04` - Sweyn II of Denmark**
- `s00` Sweyn II Estridsson  (– 28 April 1076) was King of Denmark from 1047 until his death in 1076. *(gold support)*
- `s01` He was the son of Ulf Thorgilsson and Estrid Svendsdatter, and the grandson of King Sweyn I Forkbeard through his mother's line.
- `s02` He was married three times, and fathered 20 children or more out of wedlock, including the five future kings Harald III Hen, Canute IV
- `s03` the Saint, Oluf
- `s04` I Hunger, Eric
- `s05` I Evergood, and Niels.
- `s06` He was courageous in battle, but did not have much success as a military commander.
- `s07` His skeleton reveals that he was a tall, powerfully built man who walked with a limp.

**Proposed reasoning steps (dataset order):**
1. Harald III of Denmark -> sub-answer: Sweyn II; depends on steps []
2. Sweyn II of Denmark -> sub-answer: 28 April 1076; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Sweyn II' exact]  `s00` "Sweyn II Estridsson  (– 28 April 1076) was King of Denmark from 1047 until his death in 1076."  DEPENDS_ON  `s01` "Harald III was an illegitimate son of Danish king Sweyn II Estridsson, and contested the crown with some of his brothers."

---

## 2wikimultihopqa/88be48840bda11eba7f7acde48001122  (2wikimultihopqa, compositional, hops=2)

**Question:** Where was the director of film Gamers: The Movie born?  
**Gold answer(s):** Pasadena, California

**Passage `2wikimultihopqa/88be48840bda11eba7f7acde48001122/p06` - Chris Folino**
- `s00` Christopher Peter Folino (born November 5, 1968 in Pasadena, California) is an American film director, screenwriter and producer. *(gold support)*

**Passage `2wikimultihopqa/88be48840bda11eba7f7acde48001122/p08` - Gamers: The Movie**
- `s00` Gamers:
- `s01` The Movie (or simply Gamers) is an independent 2006 mockumentary film written, directed and produced by Chris Folino. *(gold support)*
- `s02` The film follows four friends who, saddled with "four of the worst jobs known to man", attempt to set the world record for playing Demons, Nymphs, and Dragons (DND), a "Dungeons & Dragons"-like game.
- `s03` Filmed in only six days and entirely self-financed with $60,000 from credit cards, the film featured several 1980s stars in supporting roles:
- `s04` Kelly Le Brock ("Weird Science"), Beverly D'Angelo ("EntourageNational Lampoon's Vacation"), and William Katt ("The Greatest American Hero").
- `s05` The soundtrack also includes songs by Loverboy and other 1980s bands.
- `s06` Indie film web sites Indie Film Nation and bumscorner.com named "Gamers" the "Best Film of 2006.
- `s07` " It also received the award for Best Screenplay at the 2006 Melbourne Underground Film Festival.

**Proposed reasoning steps (dataset order):**
1. Gamers: The Movie -> sub-answer: Chris Folino; depends on steps []
2. Chris Folino -> sub-answer: Pasadena, California; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Chris Folino' fallback]  `s00` "Christopher Peter Folino (born November 5, 1968 in Pasadena, California) is an American film director, screenwriter and producer."  DEPENDS_ON  `s01` "The Movie (or simply Gamers) is an independent 2006 mockumentary film written, directed and produced by Chris Folino."

---

## 2wikimultihopqa/10b80bac0baf11ebab90acde48001122  (2wikimultihopqa, inference, hops=2)

**Question:** Who is Philippe Charles D'Arenberg's uncle?  
**Gold answer(s):** Philippe François, 1st Duke of Arenberg

**Passage `2wikimultihopqa/10b80bac0baf11ebab90acde48001122/p01` - Charles Eugene, 2nd Duke of Arenberg**
- `s00` Charles Eugene, 2nd Duke of Arenberg (1633–1681), a Knight of the Order of the Golden Fleece since 1678, became 2nd Duke of Arenberg in 1674 on the death of his half-brother Philippe François, 1st Duke of Arenberg. *(gold support)*
- `s01` The original title had been awarded on 6 June 1644, by Habsburg Emperor Ferdinand III, Holy Roman Emperor, making the principality of Arenberg a dukedom of the Austrian Empire..
- `s02` He married Marie-Henriette de Cusance, marquise de Varambon in 1660.
- `s03` Their two sons Philippe Charles François, 3rd Duke of Arenberg and Alexandre, fell in battle in 1691 and 1683 respectively.
- `s04` He was Grand-Bailli and Capitaine-Général of Hainaut.

**Passage `2wikimultihopqa/10b80bac0baf11ebab90acde48001122/p03` - Philippe Charles d'Arenberg**
- `s00` Philippe Charles François, 3rd Duke of Arenberg (10
- `s01` May 1663—25 August 1691) was also the 9th Duke of Aarschot.
- `s02` He became a knight of the Order of the Golden Fleece in 1685.
- `s03` Like his father, Charles Eugene, 2nd Duke of Arenberg, he was Grand-Bailiff and Captain-General of Hainaut. *(gold support)*
- `s04` The youngest general in the imperial army at the Battle of Slankamen (in modern-day Vojvodina, Serbia), he died from his wounds on August 19, 1691.
- `s05` He married Maria Enrichetta del Carretto, Marchesa de Grana e Savona in Italy, in 1684.
- `s06` He was succeeded by their son, Leopold Philippe d'Arenberg, as the 4th Duke of Arenberg, whose descendants include the current line of the Prince-Dukes d'Arenberg, as well as Empress Elisabeth of Austria and Albert I, King of the Belgians.
- `s07` His daughter Marie Anne (1689-1736) married François Egon de La Tour, Count d'Auvergne and Margrave of Berg-op-Zoom, a French "prince étranger" and nephew of the Marshal of France Turenne.
- `s08` Marie Anne's daughter Marie Henriette de La Tour d'Auvergne, Margravine of Berg-op-Zoom married John Christian, Count Palatine of Sulzbach, and was the mother of Charles Theodore, Elector of Bavaria.

**Proposed reasoning steps (dataset order):**
1. Philippe Charles d'Arenberg -> sub-answer: Charles Eugene, 2nd Duke of Arenberg; depends on steps []
2. Charles Eugene, 2nd Duke of Arenberg -> sub-answer: Philippe François, 1st Duke of Arenberg; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Charles Eugene, 2nd Duke of Arenberg' exact]  `s00` "Charles Eugene, 2nd Duke of Arenberg (1633–1681), a Knight of the Order of the Golden Fleece since 1678, became 2nd Duke of Arenberg in 1674 on the death of his half-brother Philippe François, 1st Duke of Arenberg."  DEPENDS_ON  `s03` "Like his father, Charles Eugene, 2nd Duke of Arenberg, he was Grand-Bailiff and Captain-General of Hainaut."

---

## 2wikimultihopqa/ad6dc5540baf11ebab90acde48001122  (2wikimultihopqa, inference, hops=2)

**Question:** Who is James Franklin Perry's sibling-in-law?  
**Gold answer(s):** Stephen F. Austin

**Passage `2wikimultihopqa/ad6dc5540baf11ebab90acde48001122/p04` - Emily Austin Perry**
- `s00` Emily Austin Bryan Perry (June 22, 1795 – 1851) was an early settler of Texas and sole heir to Stephen F. Austin. *(gold support)*
- `s01` She achieved significant political, economic and social status as a woman in Texas at a time when women were often not treated equal to men.

**Passage `2wikimultihopqa/ad6dc5540baf11ebab90acde48001122/p06` - James Franklin Perry**
- `s00` James Franklin Perry (1790–1853) was an American who was an early settler and prominent citizen of Texas.
- `s01` James married Emily Austin Perry, operated Peach Point Plantation, and was involved in Texas land distribution. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. James Franklin Perry -> sub-answer: Emily Austin Perry; depends on steps []
2. Emily Austin Perry -> sub-answer: Stephen F. Austin; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Emily Austin Perry' fallback]  `s00` "Emily Austin Bryan Perry (June 22, 1795 – 1851) was an early settler of Texas and sole heir to Stephen F. Austin."  DEPENDS_ON  `s01` "James married Emily Austin Perry, operated Peach Point Plantation, and was involved in Texas land distribution."

---

## hotpotqa/5ac09d265542992a796ded39  (hotpotqa, bridge, hops=2)

**Question:** Erving Goffman was cited as higher than a literary critic on which guide?  
**Gold answer(s):** The Times Higher Education Guide

**Passage `hotpotqa/5ac09d265542992a796ded39/p06` - Erving Goffman**
- `s00` Erving Goffman (11 June 1922 – 19 November 1982) was a Canadian-American sociologist and writer, considered by some "the most influential American sociologist of the twentieth century". *(gold support)*
- `s01` In 2007 he was listed by "The Times Higher Education Guide" as the sixth most-cited author in the humanities and social sciences, behind Anthony Giddens, Pierre Bourdieu and Michel Foucault, and ahead of Jürgen Habermas. *(gold support)*

**Passage `hotpotqa/5ac09d265542992a796ded39/p09` - Michel Foucault**
- `s00` Paul-Michel Foucault (15 October 1926 – 25 June 1984), generally known as Michel Foucault (] ), was a French philosopher, historian of ideas, social theorist, and literary critic. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Erving Goffman -> sub-answer: Michel Foucault; depends on steps []
2. Michel Foucault -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Michel Foucault' exact]  `s00` "Paul-Michel Foucault (15 October 1926 – 25 June 1984), generally known as Michel Foucault (] ), was a French philosopher, historian of ideas, social theorist, and literary critic."  DEPENDS_ON  `s01` "In 2007 he was listed by "The Times Higher Education Guide" as the sixth most-cited author in the humanities and social sciences, behind Anthony Giddens, Pierre Bourdieu and Michel Foucault, and ahead of Jürgen Habermas."

---

## hotpotqa/5a73354f5542991f9a20c687  (hotpotqa, bridge, hops=2)

**Question:** Thomas Henry Moray Followed work down on nuclear batteries in 1912 by this English physicist?  
**Gold answer(s):** Henry Moseley

**Passage `hotpotqa/5a73354f5542991f9a20c687/p08` - Thomas Henry Moray**
- `s00` Thomas Henry Moray (August 28, 1892 - May 18, 1974) was an inventor from Salt Lake City, Utah. *(gold support)*
- `s01` He received a US patent 2,460,707 in February 1949, after a process of 17 years in discussions with the patent office.
- `s02` The main components of the patent were an LC circuit resonator and a set of vacuum power tubes of diode type using uranium and radium power sources and doped germanium semiconductors on the cathodes.
- `s03` It was an early example of doped semiconductors and a forerunner of radioactive power supplies using radioactive isotopes in space research.
- `s04` Moray's device followed other work on nuclear batteries first done in 1913 by Henry Moseley using a radium source. *(gold support)*

**Passage `hotpotqa/5a73354f5542991f9a20c687/p09` - Henry Moseley**
- `s00` Henry Gwyn Jeffreys Moseley (23 November 1887 – 10 August 1915) was an English physicist, whose contribution to the science of physics was the justification from physical laws of the previous empirical and chemical concept of the atomic number. *(gold support)*
- `s01` This stemmed from his development of Moseley's law in X-ray spectra.
- `s02` Moseley's Law justified many concepts in chemistry by sorting the chemical elements of the periodic table of the elements in a logical order based on their physics.
- `s03` He published first the Long Form periodic table or Modern periodic table which is used till date.

**Proposed reasoning steps (dataset order):**
1. Thomas Henry Moray -> sub-answer: Henry Moseley; depends on steps []
2. Henry Moseley -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Henry Moseley' fallback]  `s00` "Henry Gwyn Jeffreys Moseley (23 November 1887 – 10 August 1915) was an English physicist, whose contribution to the science of physics was the justification from physical laws of the previous empirical and chemical concept of the atomic number."  DEPENDS_ON  `s04` "Moray's device followed other work on nuclear batteries first done in 1913 by Henry Moseley using a radium source."

---

## hotpotqa/5ae4b5935542995ad6573e27  (hotpotqa, comparison, hops=2)

**Question:** Which of these artist lives closer to Canada, Koshi Inaba or Jonathan Davis?  
**Gold answer(s):** Jonathan Howsmon Davis

**Passage `hotpotqa/5ae4b5935542995ad6573e27/p03` - Koshi Inaba**
- `s00` Koshi Inaba (稲葉浩志 , Inaba Kōshi ) , born Hiroshi Inaba (稲葉浩志 , Inaba Hiroshi ) on September 23, 1964 in Tsuyama, Okayama, is a Japanese vocalist, multi-instrumentalist and songwriter. *(gold support)*

**Passage `hotpotqa/5ae4b5935542995ad6573e27/p07` - Jonathan Davis**
- `s00` Jonathan Howsmon Davis (born January 18, 1971), also known as JD and JDevil (or J Devil), is an American musician best known as the leading vocalist and frontman of the nu metal band Korn. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Koshi Inaba -> sub-answer: None; depends on steps []
2. Jonathan Davis -> sub-answer: None; depends on steps []

**Proposed dependency edges:**
- (none proposed)

---

## hotpotqa/5ae083e855429924de1b70fb  (hotpotqa, bridge, hops=2)

**Question:** By how many points did Dion Lewis' team trail by, in the third quarter, of the Super Bowl that they won ?   
**Gold answer(s):** 25 points

**Passage `hotpotqa/5ae083e855429924de1b70fb/p01` - Super Bowl LI**
- `s00` Super Bowl LI was an American football game played at NRG Stadium in Houston, Texas, on Sunday, February 5, 2017, to determine the champion of the National Football League (NFL) for the 2016 season.
- `s01` The American Football Conference (AFC) champion New England Patriots, after trailing by as many as 25 points (28-3) during the third quarter, defeated the National Football Conference (NFC) champion Atlanta Falcons, 34–28 in overtime. *(gold support)*
- `s02` The Patriots' 25-point comeback is the largest comeback in Super Bowl history, and Super Bowl LI was the first to be decided in overtime.

**Passage `hotpotqa/5ae083e855429924de1b70fb/p08` - Dion Lewis**
- `s00` Dion John Lewis (born September 27, 1990) is an American football running back for the New England Patriots of the National Football League (NFL).
- `s01` He was drafted by the Philadelphia Eagles in the fifth round of the 2011 NFL Draft.
- `s02` With the Patriots, he won Super Bowl LI over the Atlanta Falcons. *(gold support)*
- `s03` He played college football at the University of Pittsburgh.
- `s04` Lewis has also played for the Cleveland Browns and Indianapolis Colts.
- `s05` His Patriots teammate, receiver Julian Edelman, has nicknamed Lewis both "Jitterbug" and "Little Dirty".
- `s06` Lewis had not played for two seasons before signing with the Patriots in 2015, and was a significant contributor to the New England offense before a season-ending knee injury in Week 9 put him out of the line-up.
- `s07` Two reconstructive surgeries on his damaged knee kept him sidelined until part way through the 2016 season, his return on November 12, 2016 made a direct impact; his career-defining performance coming in the Patriots over the Houston Texans, where Lewis had 188 all-purpose yards and became the first player in NFL history to score a touchdown on a rush, a reception, and a kick return during the same playoff game.
- `s08` Notably, as of the end of the 2016-2017 season, Lewis has never played in a game which the Patriots have subsequently lost.

**Proposed reasoning steps (dataset order):**
1. Dion Lewis -> sub-answer: Super Bowl LI; depends on steps []
2. Super Bowl LI -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Super Bowl LI' exact]  `s00` "Super Bowl LI was an American football game played at NRG Stadium in Houston, Texas, on Sunday, February 5, 2017, to determine the champion of the National Football League (NFL) for the 2016 season."  DEPENDS_ON  `s02` "With the Patriots, he won Super Bowl LI over the Atlanta Falcons."

---

## hotpotqa/5ae55a4e5542990ba0bbb285  (hotpotqa, bridge, hops=2)

**Question:**  "JK Wedding Entrance Dance" is a viral video that uses a song by a rapper whose first album was certified what?  
**Gold answer(s):** double platinum

**Passage `hotpotqa/5ae55a4e5542990ba0bbb285/p07` - Chris Brown**
- `s00` Christopher Maurice Brown (born May 5, 1989) is an American singer, songwriter, actor, and rapper. *(gold support)*
- `s01` Born in 1989 in Tappahannock, Virginia, he was involved in his church choir and several local talent shows from a young age.
- `s02` Having signed with Jive Records in 2004, Brown released his self-titled debut studio album the following year.
- `s03` It peaked at number two on the US "Billboard" 200 and was later certified double platinum by the Recording Industry Association of America (RIAA), selling an overall three million copies worldwide. *(gold support)*
- `s04` With his first single "Run It!
- `s05` " peaking atop the US "Billboard" Hot 100, Brown became the first male artist as a lead since Diddy in 1997 to have his debut single top the chart.
- `s06` His second album "Exclusive" (2007) spawned his second Hot 100 number one "Kiss Kiss", in addition to "With You" and "Forever".
- `s07` The album was also certified double platinum by the RIAA.
- `s08` In addition to his solo commercial success, Brown has been featured on several singles such as "No Air", a duet with singer Jordin Sparks, "Shortie like Mine" with the rapper Bow Wow and "Shawty Get Loose" alongside Lil Mama and T-Pain.
- `s09` The songs have peaked at number three, number nine and number ten on the US "Billboard" Hot 100 respectively.

**Passage `hotpotqa/5ae55a4e5542990ba0bbb285/p09` - JK Wedding Entrance Dance**
- `s00` "JK Wedding Entrance Dance" is a viral video originally uploaded to YouTube on July 19, 2009, featuring the wedding of Jill Peterson and Kevin Heinz, using "Forever" by Chris Brown as the song for their wedding march. *(gold support)*
- `s01` In its first 48 hours, the video was viewed more than 3.5 million times.
- `s02` The original upload of the video was the 3rd most popular video on YouTube in 2009, and as of September 2016 had been viewed over around 93.4 million times.
- `s03` "Time" magazine ranked the video at number fifteen on its list of the fifty greatest YouTube videos.

**Proposed reasoning steps (dataset order):**
1. JK Wedding Entrance Dance -> sub-answer: Chris Brown; depends on steps []
2. Chris Brown -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Chris Brown' fallback]  `s00` "Christopher Maurice Brown (born May 5, 1989) is an American singer, songwriter, actor, and rapper."  DEPENDS_ON  `s00` ""JK Wedding Entrance Dance" is a viral video originally uploaded to YouTube on July 19, 2009, featuring the wedding of Jill Peterson and Kevin Heinz, using "Forever" by Chris Brown as the song for their wedding march."

---

## hotpotqa/5ab521575542996a3a96a02e  (hotpotqa, comparison, hops=2)

**Question:** Is Xingcheng or Ulan Hot located in the Inner Mongolia region of China?  
**Gold answer(s):** Ulanhot

**Passage `hotpotqa/5ab521575542996a3a96a02e/p06` - Xingcheng**
- `s00` Xingcheng (), former name Ningyuan (宁远), is a county-level city of southwest Liaoning province, China, with a population of approximately 140,000 urban inhabitants, and is located on the Liaodong Bay, i.e. the northern coast of the Bohai Sea. *(gold support)*
- `s01` Currently under the administration of Huludao City, the area is steeped in history, and contains one of the best preserved Ming Dynasty towns in China, as well as functioning as a laidback summer resort.

**Passage `hotpotqa/5ab521575542996a3a96a02e/p09` - Ulan Hot**
- `s00` Ulanhot (Mongolian: ; Cyrillic: Улаан хот ; Latin transliteration: "Ulaγan qota"; ), formerly known as Wangin Süm, alternatively Wang-un Süme, Ulayanqota (Red City) in Classical Mongolian, and Wangyehmiao or Wangyemiao () in Chinese prior to 1947, is a county-level city and the administrative center of Hinggan League in the East of Inner Mongolia autonomous region. *(gold support)*
- `s01` Between the years 1947 and 1950, Ulanhot was the capital of Inner Mongolia Region.
- `s02` In 1950, the capital moved to Zhangjiakou and then again in 1952 it moved to Hohhot, which remains the capital to this day.

**Proposed reasoning steps (dataset order):**
1. Xingcheng -> sub-answer: None; depends on steps []
2. Ulan Hot -> sub-answer: None; depends on steps []

**Proposed dependency edges:**
- (none proposed)

---

## hotpotqa/5ac4f33355429924173fb507  (hotpotqa, bridge, hops=2)

**Question:** where is the Vanderbilt mansion which Ochre Point–Cliffs Historic District is its home located   
**Gold answer(s):** Ochre Point Avenue

**Passage `hotpotqa/5ac4f33355429924173fb507/p02` - The Breakers**
- `s00` The Breakers is a Vanderbilt mansion located on Ochre Point Avenue, Newport, Rhode Island, United States on the Atlantic Ocean. *(gold support)*
- `s01` The building became a National Historic Landmark in 1994, and is a contributing property to the Bellevue Avenue Historic District.
- `s02` It is owned and operated by the Preservation Society of Newport County and is open for visitation on a year-round basis.

**Passage `hotpotqa/5ac4f33355429924173fb507/p05` - Ochre Point–Cliffs Historic District**
- `s00` The Ochre Point–Cliffs Historic District is a historic district in Newport, Rhode Island.
- `s01` The district includes a significant subset of the Bellevue Avenue Historic District, a National Historic Landmark District, including all of the major Gilded Age mansions on the waterfront facing Easton Bay between Memorial Boulevard and Marine Avenue.
- `s02` The district is home to famous mansions such as the William Watts Sherman House and The Breakers, one of the largest houses in the area built by the Vanderbilt Family. *(gold support)*
- `s03` The district was added to the National Register of Historic Places in 1975.

**Proposed reasoning steps (dataset order):**
1. Ochre Point–Cliffs Historic District -> sub-answer: The Breakers; depends on steps []
2. The Breakers -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'The Breakers' exact]  `s00` "The Breakers is a Vanderbilt mansion located on Ochre Point Avenue, Newport, Rhode Island, United States on the Atlantic Ocean."  DEPENDS_ON  `s02` "The district is home to famous mansions such as the William Watts Sherman House and The Breakers, one of the largest houses in the area built by the Vanderbilt Family."

---

## hotpotqa/5a73024f5542991f9a20c5fc  (hotpotqa, bridge, hops=2)

**Question:** what year was the cover artist of Multiverse: Exploring Poul Anderson's Worlds born ?  
**Gold answer(s):** September 13, 1960

**Passage `hotpotqa/5a73024f5542991f9a20c5fc/p04` - Bob Eggleton**
- `s00` Bobera Eggleton (born September 13, 1960) is an American science fiction, fantasy, and horror artist. *(gold support)*
- `s01` Eggleton has been honored with the Hugo Award for Best Professional Artist eight times, first winning in 1994.
- `s02` He also won the Hugo Award for Best Related Book in 2001 for his art book "Greetings From Earth".
- `s03` He has also won the Chesley Award for Artistic Achievement in 1999 and was the guest of honor at Chicon 2000.

**Passage `hotpotqa/5a73024f5542991f9a20c5fc/p05` - Multiverse: Exploring Poul Anderson's Worlds**
- `s00` Multiverse: Exploring Poul Anderson's Worlds is a gedenkschrift honoring science fiction and fantasy author Poul Anderson, in the form of an anthology of short stories and tributes edited by Greg Bear and Gardner Dozois.
- `s01` The book also includes cover art and interior illustrations by Bob Eggleton. *(gold support)*
- `s02` It was first published in hardcover in May 2014 by Subterranean Press, with simultaneous paperback and ebook editions issued in June 2015 by Baen Books.
- `s03` All but one of the pieces are original to the anthology; the remaining one, Tad Williams's "Three Lilies and Three Leopards (And a Participation Ribbon in Science)", was originally published in the Winter 2012 issue of the ejournal "Subterreanean Online".

**Proposed reasoning steps (dataset order):**
1. Multiverse: Exploring Poul Anderson's Worlds -> sub-answer: Bob Eggleton; depends on steps []
2. Bob Eggleton -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Bob Eggleton' fallback]  `s00` "Bobera Eggleton (born September 13, 1960) is an American science fiction, fantasy, and horror artist."  DEPENDS_ON  `s01` "The book also includes cover art and interior illustrations by Bob Eggleton."

---

## hotpotqa/5adff4a555429925eb1afb91  (hotpotqa, comparison, hops=2)

**Question:** Which airport is closer to the Atlantic ocean: Wilmington International Airport, or Texarkana Regional Airport?  
**Gold answer(s):** Wilmington International Airport

**Passage `hotpotqa/5adff4a555429925eb1afb91/p00` - Wilmington International Airport**
- `s00` Wilmington International Airport (IATA: ILM, ICAO: KILM, FAA LID: ILM) is a public airport located just north of Wilmington, North Carolina, in unincorporated Wrightsboro, Cape Fear Township, New Hanover County. *(gold support)*

**Passage `hotpotqa/5adff4a555429925eb1afb91/p05` - Texarkana Regional Airport**
- `s00` Texarkana Regional Airport (IATA: TXK, ICAO: KTXK, FAA LID: TXK) , also known as Webb Field, is a public use airport located three nautical miles (6 km) northeast of the central business district of Texarkana, a city in Miller County, Arkansas, United States. *(gold support)*
- `s01` It is owned by the Texarkana Airport Authority.
- `s02` The airport is located within the city limits of Texarkana, roughly 3 miles east of State Line Avenue.
- `s03` The front gate opens to the northwest, at the intersection of Arkansas Boulevard and U.S. Route 67.
- `s04` A Union Pacific Railroad line runs parallel to US 67 on the side of the highway facing the airport.
- `s05` It is mostly used for general aviation, but is also served by American Eagle.

**Proposed reasoning steps (dataset order):**
1. Wilmington International Airport -> sub-answer: None; depends on steps []
2. Texarkana Regional Airport -> sub-answer: None; depends on steps []

**Proposed dependency edges:**
- (none proposed)

---

## hotpotqa/5a716dc15542994082a3e82b  (hotpotqa, bridge, hops=2)

**Question:** Who is younger Kirk Humphreys or Tom Coburn?  
**Gold answer(s):** Kirk Humphreys

**Passage `hotpotqa/5a716dc15542994082a3e82b/p00` - Tom Coburn**
- `s00` Thomas Allen "Tom" Coburn (born March 14, 1948) is an American politician and medical doctor. *(gold support)*
- `s01` A member of the Republican Party, he was the junior United States Senator from Oklahoma.

**Passage `hotpotqa/5a716dc15542994082a3e82b/p01` - Kirk Humphreys**
- `s00` Kirk Humphreys (born September 13, 1950) is an American politician who served as Mayor of Oklahoma City from April 9, 1998 to November 3, 2003. *(gold support)*
- `s01` He was considered a favorite candidate of the Republican party establishment for U.S. Senator in 2004, losing to former Congressman Tom Coburn, MD in the primary.
- `s02` Humphreys is the chairman of The Humphreys Company.

**Proposed reasoning steps (dataset order):**
1. Kirk Humphreys -> sub-answer: Tom Coburn; depends on steps []
2. Tom Coburn -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Tom Coburn' exact]  `s00` "Thomas Allen "Tom" Coburn (born March 14, 1948) is an American politician and medical doctor."  DEPENDS_ON  `s01` "He was considered a favorite candidate of the Republican party establishment for U.S. Senator in 2004, losing to former Congressman Tom Coburn, MD in the primary."

---

## hotpotqa/5ab946d7554299743d22eaaf  (hotpotqa, bridge, hops=2)

**Question:** What is the rank of the incumbent that RJ Harris challenged in 2010?  
**Gold answer(s):** the fourth-ranking Republican leader in the House

**Passage `hotpotqa/5ab946d7554299743d22eaaf/p03` - Tom Cole**
- `s00` Thomas Jeffery Cole (born April 28, 1949) is the U.S. Representative for Oklahoma 's 4 congressional district , serving since 2003.
- `s01` He is a member of the Republican Party.
- `s02` He is a Deputy Majority Whip.
- `s03` The chairman of the National Republican Congressional Committee (NRCC) from 2006 to 2008, he was, during his tenure, the fourth-ranking Republican leader in the House. *(gold support)*
- `s04` As of 2015, Cole – a member of the Chickasaw Nation – is one of only two registered Native Americans in Congress (the other being fellow Oklahoman Markwayne Mullin).

**Passage `hotpotqa/5ab946d7554299743d22eaaf/p05` - R. J. Harris**
- `s00` Richard Jason Satawk "R. J." Harris (born November 16, 1972) is a United States Army National Guard warrant officer, politician, law student and former Air Traffic Controller.
- `s01` He was a candidate for the Libertarian Party's 2012 nomination for President of the United States.
- `s02` In 2010, he unsuccessfully challenged incumbent Tom Cole for the Republican Party nomination in the primary election for Oklahoma's 4th congressional district. *(gold support)*
- `s03` He ran as an independent candidate for the same congressional seat in 2012.

**Proposed reasoning steps (dataset order):**
1. R. J. Harris -> sub-answer: Tom Cole; depends on steps []
2. Tom Cole -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Tom Cole' fallback]  `s03` "The chairman of the National Republican Congressional Committee (NRCC) from 2006 to 2008, he was, during his tenure, the fourth-ranking Republican leader in the House."  DEPENDS_ON  `s02` "In 2010, he unsuccessfully challenged incumbent Tom Cole for the Republican Party nomination in the primary election for Oklahoma's 4th congressional district."

---

## hotpotqa/5ac24cc45542996366519963  (hotpotqa, comparison, hops=2)

**Question:** Both Andrew and Jeremy Get Married and The Last Lions are what type of films?  
**Gold answer(s):** documentary film

**Passage `hotpotqa/5ac24cc45542996366519963/p07` - The Last Lions**
- `s00` The Last Lions is a 2011 African nature documentary film by National Geographic Society, videotaped and directed by Dereck and Beverly Joubert. *(gold support)*
- `s01` It was shot at the Okavango Delta in Botswana.
- `s02` The film premiered at the Palm Springs International Film Festival in January 2011 and was released in select theaters on February 18, 2011.
- `s03` The film follows in the tradition of other National Geographic big cat films, such as "India: Land of the Tiger" and "Eye of the Leopard".

**Passage `hotpotqa/5ac24cc45542996366519963/p08` - Andrew and Jeremy Get Married**
- `s00` Andrew and Jeremy Get Married is a 2004 British documentary film written and directed by Don Boyd for the BBC. *(gold support)*
- `s01` It tells the story of two Englishmen, Andrew Thomas and Jeremy Trafford, as they plan for their commitment ceremony.
- `s02` Originally commissioned for the "BBC Storyville" series, the film premiered at the 2004 Toronto International Film Festival.

**Proposed reasoning steps (dataset order):**
1. Andrew and Jeremy Get Married -> sub-answer: None; depends on steps []
2. The Last Lions -> sub-answer: None; depends on steps []

**Proposed dependency edges:**
- (none proposed)

---

## hotpotqa/5a72239a55429971e9dc92cf  (hotpotqa, bridge, hops=2)

**Question:** Who was soldier Archie A. Peck's commanding officer during the Meuse-Argonne Offensive?  
**Gold answer(s):** Major Charles White Whittlesey

**Passage `hotpotqa/5a72239a55429971e9dc92cf/p01` - Lost Battalion (World War I)**
- `s00` The Lost Battalion is the name given to nine companies of the United States 77th Division, roughly 554 men, isolated by German forces during World War I after an American attack in the Argonne Forest in October 1918. *(gold support)*
- `s01` Roughly 197 were killed in action and approximately 150 missing or taken prisoner before 194 remaining men were rescued.
- `s02` They were led by Major Charles White Whittlesey. *(gold support)*
- `s03` On 2 October, the division quickly advanced into the Argonne, under the belief that French forces were supporting the left flank and two American units including the 92nd Division were supporting the right flank.
- `s04` Unknown to Whittlesey's unit, the French advance had been stalled.
- `s05` Without this knowledge, the Americans had moved beyond the rest of the Allied line and found themselves completely cut off and surrounded by German forces.
- `s06` For the next six days, suffering heavy losses, the men of the division were forced to fight off several attacks by the Germans.

**Passage `hotpotqa/5a72239a55429971e9dc92cf/p08` - Archie A. Peck**
- `s00` Archie A. Peck (November 22, 1894 – September 15, 1978) was a soldier in the United States Army who received the Medal of Honor for his actions during World War I. *(gold support)*
- `s01` While serving as a private foot soldier in the US 77th Division during the Meuse-Argonne Offensive, his unit ended up with several others behind German lines, in what was later known as "the Lost Battalion". *(gold support)*
- `s02` This was the bloodiest battle of the war involving US troops.
- `s03` Peck acted gallantly in the surrounding unit, saving two wounded men under machine gun fire.

**Proposed reasoning steps (dataset order):**
1. Archie A. Peck -> sub-answer: Lost Battalion; depends on steps []
2. Lost Battalion (World War I) -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [B_derived_exact_anchor, anchor 'Lost Battalion' exact]  `s00` "The Lost Battalion is the name given to nine companies of the United States 77th Division, roughly 554 men, isolated by German forces during World War I after an American attack in the Argonne Forest in October 1918."  DEPENDS_ON  `s01` "While serving as a private foot soldier in the US 77th Division during the Meuse-Argonne Offensive, his unit ended up with several others behind German lines, in what was later known as "the Lost Battalion"."

---

## hotpotqa/5ab720685542993667793f44  (hotpotqa, bridge, hops=2)

**Question:** What type of believer does Mir Jafar Baghirov and Joseph Stalin have in common?  
**Gold answer(s):** communist

**Passage `hotpotqa/5ab720685542993667793f44/p00` - Joseph Stalin**
- `s00` Joseph Vissarionovich Stalin (18 December 1878 – 5 March 1953) was a Georgian-born Soviet revolutionary and political leader.
- `s01` Governing the Soviet Union as its dictator from the mid-1920s until his death in 1953, he served as General Secretary of the Central Committee of the Communist Party of the Soviet Union from 1922 to 1952 and as Premier of the Soviet Union from 1941 to 1953. *(gold support)*
- `s02` Ideologically a Marxist and a Leninist, Stalin helped to formalise these ideas as Marxism–Leninism while his own policies became known as Stalinism.

**Passage `hotpotqa/5ab720685542993667793f44/p09` - Mir Jafar Baghirov**
- `s00` Mir Jafar Baghirov Abbas oglu (Azerbaijani: "Mir Cəfər Bağırov Abbas oğlu" ; 17 September 1896 – 7 May 1956) was the communist leader of the Azerbaijan SSR from 1932 to 1953, under the Soviet leadership of Joseph Stalin. *(gold support)*

**Proposed reasoning steps (dataset order):**
1. Mir Jafar Baghirov -> sub-answer: Joseph Stalin; depends on steps []
2. Joseph Stalin -> sub-answer: None; depends on steps [1]

**Proposed dependency edges:**
- `e0` [C_derived_fallback_anchor, anchor 'Joseph Stalin' fallback]  `s01` "Governing the Soviet Union as its dictator from the mid-1920s until his death in 1953, he served as General Secretary of the Central Committee of the Communist Party of the Soviet Union from 1922 to 1952 and as Premier of the Soviet Union from 1941 to 1953."  DEPENDS_ON  `s00` "Mir Jafar Baghirov Abbas oglu (Azerbaijani: "Mir Cəfər Bağırov Abbas oğlu" ; 17 September 1896 – 7 May 1956) was the communist leader of the Azerbaijan SSR from 1932 to 1953, under the Soviet leadership of Joseph Stalin."

---

## hotpotqa/5a7b215f55429931da12c9e3  (hotpotqa, comparison, hops=2)

**Question:** Who was born first Cid Corman or Elswyth Thane?  
**Gold answer(s):** Helen Elswyth Thane Ricker Beebe

**Passage `hotpotqa/5a7b215f55429931da12c9e3/p03` - Cid Corman**
- `s00` Cid (Sidney) Corman (June 29, 1924 – March 12, 2004) was an American poet, translator and editor, most notably of "Origin", who was a key figure in the history of American poetry in the second half of the 20th century. *(gold support)*

**Passage `hotpotqa/5a7b215f55429931da12c9e3/p07` - Elswyth Thane**
- `s00` Helen Elswyth Thane Ricker Beebe (May 16, 1900 – July 31, 1984) was an American romance novelist. *(gold support)*
- `s01` Born in Burlington, Iowa, she was the daughter of a local teacher and high school principal.
- `s02` The family moved to New York City in 1918, and "Helen Ricker" changed her name to "Elswyth Thane".
- `s03` She began working as a freelance writer in the 20s, and became a newspaper writer and a Hollywood screenwriter.
- `s04` Her first novel, "Riders of the Wind", was published in 1926.
- `s05` Her novel, "The Tudor Wench", about Elizabeth I of England, was made into a play.
- `s06` She was a collector of scarves.

**Proposed reasoning steps (dataset order):**
1. Cid Corman -> sub-answer: None; depends on steps []
2. Elswyth Thane -> sub-answer: None; depends on steps []

**Proposed dependency edges:**
- (none proposed)

---

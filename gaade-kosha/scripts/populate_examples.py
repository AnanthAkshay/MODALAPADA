# -*- coding: utf-8 -*-
"""
Populate team-drafted example sentences for Gaade Kosha (Problem 2).
Fills the previously empty `example` column in data/gaades.csv with a
natural conversational or narrative example in English for each canonical gaade.
Also updates data/gaade_provenance.csv with example_source = 'team_drafted'.
"""

import os
import csv
import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
GAADES_CSV = DATA_DIR / "gaades.csv"
PROVENANCE_CSV = DATA_DIR / "gaade_provenance.csv"
BACKUP_DIR = DATA_DIR / "backups"

# Dictionary of 226 realistic conversational / narrative examples
EXAMPLES = {
    # G001 - G025
    "G001": "Seeing his brother risk all his monthly earnings on an unverified lottery scheme after already winning a decent payout, Anand warned him, 'Ati aase gati kedu; don't ruin yourself chasing impossible greed.'",
    "G002": "After working sixteen hours a day in the sun building his small furniture workshop, Basavaraj happily served sweets to his family, reminding them that kai kesaradare baayi mosaru.",
    "G003": "When the supervisor was caught secretly shifting his own accounting blunders onto the apprentice, the director fired him immediately, saying that in the end, maadiddunno maharaya.",
    "G004": "Observing her nephew throw violent tantrums whenever denied toys, Suma advised his mother, 'Gidavaagi baggaddu maravaagi baggeethe? Discipline him gently now while his character is still forming.'",
    "G005": "By setting aside just fifty rupees each day in a small ceramic jar, the college student bought his semester textbooks without asking his parents, demonstrating hani hani koodi halla.",
    "G006": "Despite enduring months of project delays and client criticism without losing his temper, the architect finally won the state contract, proving that thaalidavanu baaliyaanu.",
    "G007": "When his colleagues took out expensive car loans to show off in the office, Chandrashekhar chose a modest scooter, advising them to always cut their coat according to their cloth.",
    "G008": "In his impatience to overtake three lorries on a wet hairpin curve, the cab driver skidded into a ditch, illustrating that avasarave apaghaatakke kaarana.",
    "G009": "Having devoted hours every weekend to mentoring underprivileged kids, Raghav was delighted when the community honored his selfless work, knowing that as you sow, so you reap.",
    "G010": "While his competitors spent three months deliberating on contract fine print, the swift entrepreneur launched the mobile app, remarking that time and tide wait for no man.",
    "G011": "Reflecting on his lost college years spent loafing instead of studying for competitive exams, Ramesh sighed, 'Hoda kaala matte baaradu; lost hours never come back.'",
    "G012": "During the formal village council assembly, the young urban researcher dressed respectfully in a traditional dhoti and folded his hands, following the wisdom of kaalakke thakka kola.",
    "G013": "Seeing her exhausted son ready to give up after failing his medical mock test, the mother placed a glass of milk before him and said, 'Kashtavillade phalavilla; sweet results require sweat.'",
    "G014": "Even after retiring as a chief engineer, Gowda cleaned his own tool shed and fixed neighborhood water pumps with pride, firmly believing that kelasave kailaasa.",
    "G015": "Instead of delivering another passionate speech about cleaning the temple premises, the youth leader picked up a broom and began sweeping, proving that maathigintha kruti melu.",
    "G016": "When her sister suggested filing their income tax returns on the final due date, Deepa sat at the laptop immediately, insisting, 'Never postpone a day's work to tomorrow.'",
    "G017": "His uncle scolded the idle youth sitting under the banyan tree waiting for government grants, stating bluntly, 'Folded hands and sitting idle will never feed an empty stomach.'",
    "G018": "Though the soil was rocky and irrigation scarce, the persistent farmer dug three trenches and planted millets, confident that genuine effort always yields its rightful reward.",
    "G019": "When heavy landslides blocked the main highway to the district hospital, the determined ambulance driver navigated an unpaved forest trail, showing that guri iddavange daari siguttade.",
    "G020": "Surviving three devastating drought seasons before harvesting bumper sugarcane this autumn reminded the farming family that sweet comfort always follows bitter hardship.",
    "G021": "By preparing a flawless, detailed blueprint on day one, the engineering squad completed the rural bridge two weeks ahead of schedule, proving that a good beginning is half the task.",
    "G022": "Spraying pesticide at the exact moment the insect larvae emerged saved the grape harvest, confirming that work done at the proper hour alone is truly fruitful.",
    "G023": "The storekeeper scrambled to buy flood barriers only after muddy rainwater rushed through his cellar door, prompting neighbors to remark on opening an umbrella after the storm.",
    "G024": "When the municipal water tanker finally arrived four hours after the kitchen fire had already burnt the hut to ashes, villagers scoffed that Hanumappa arrived after the town burned.",
    "G025": "Forgetting to buy salt until the sambar was already boiling over the woodfire made everyone laugh at remembering cooking only after the stove is ablaze.",

    # G026 - G050
    "G026": "Having already lost his security deposit to a fake housing broker last year, Naveen refused to wire any cash without a signed deed, refusing to fall into a day-seen well at night.",
    "G027": "When offered a sponsored scholarship to study abroad, Swathi signed the agreement on the same afternoon, knowing one must never let go of an opportunity that lands in one's hands.",
    "G028": "Standing firm before the unexpected audit committee without panic or trembling, the bank manager handled every tough query with composure, prepared to face whatever comes.",
    "G029": "Unlike the junior associate who boasted loudly at the cafeteria table, the senior scientist listened quietly and answered only when asked, behaving like a full pot that never spills.",
    "G030": "The renowned classical singer bowed deeply to touch the feet of his elderly guru before accepting his national medal, exemplifying the tree that bends lower as its fruit ripens.",
    "G031": "By trying to outsmart the income tax department with three layers of fabricated shell invoices, the greedy merchant landed in prison, undone by his own over-cleverness.",
    "G032": "Disillusioned by the relentless traffic and solitary cubicle life in the metropolis, Karthik recalled his father's words: 'Distant mountains always appear deceptively smooth to the eye.'",
    "G033": "After being sidelined on the sports bench for three years, the substitute striker scored the tournament-winning goal, proving that when the right moment arrives, even stones will speak.",
    "G034": "To the stranded trekker lost in the Western Ghats for thirty hours, a simple packet of cold beaten rice offered by a villager tasted like a feast from heaven.",
    "G035": "Living happily in a small tiled roof cottage without chasing flashy cars or status symbols, the elderly postman enjoyed profound inner peace, content with whatever he possessed.",
    "G036": "Warned by his accountant that expanding to four new cities on borrowed capital was reckless, the founder hesitated, recognizing that ambitious desire must respect realistic limits.",
    "G037": "Whether sweeping the courtyard at sunrise or bookkeeping late into the night, the honest artisan poured devotion into every stroke, honoring work as sacred worship.",
    "G038": "Once elected town councillor, the young politician immediately stopped answering calls from the volunteers who had campaigned for him, shamelessly kicking away the ladder he climbed.",
    "G039": "Blistered hands and sleepless nights spent practicing coding problems paid off when Sheela received her offer letter, proving that enduring hardship brings its reward.",
    "G040": "Realizing that customers now preferred digital payments over cash, the traditional provision merchant installed a QR scanner, adapting wisely to changing times.",
    "G041": "When his nephew tried to prepare for entrance exams while simultaneously running an online gaming channel, his uncle insisted on completing one task for one time.",
    "G042": "Instead of trading insults with the aggressive driver who dented his bumper, Madhav quietly took photos and contacted the insurer, showing that patience prevents greater turmoil.",
    "G043": "Consistently supplying fresh, unadulterated milk to the colony earned the dairy farmer generations of loyal patrons, demonstrating that righteous deeds bring sweet outcomes.",
    "G044": "Watching the golden paddy fields sway gently in the breeze, the proud farmer told his sons that only sweat poured into the soil brings rich harvests.",
    "G045": "Appreciate the fresh coconut water while the tree is bearing fruit right before your eyes; value blessings when they are within reach.",
    "G046": "Seeing mighty emperors and wealthy dynasties fade into obscure history reminds us all to bow humbly before the inexorable power of time.",
    "G047": "Wasting his prime youth sleeping until noon and refusing apprentice jobs, the idle lad soon found his pantry empty, confirming that sloth is the root of destitution.",
    "G048": "Stepping forward to support his sick father's household without complaint, the young man demonstrated that honest labor and duty are the true marks of dignity.",
    "G049": "By uniting all sixty families in the hamlet to build a check-dam before monsoon, the villagers prevented drought, proving that strength lies in unbroken unity.",
    "G050": "Lifting the heavy collapsed roof beam became simple when ten neighbors grabbed hold together, confirming that work shared among ten people becomes light as a feather.",

    # G051 - G075
    "G051": "While fair-weather acquaintances vanished the moment his shop caught fire, the quiet neighbor arrived with dry provisions and shelter, proving that a true relative is one who stands by in disaster.",
    "G052": "When everyone else distanced themselves after his bankruptcy, Srinivas remained by his side and helped him draft a recovery plan, showing that a real friend arrives in dark times.",
    "G053": "In mediating the dispute between the two brothers, the elder pointed out that an argument never sustains itself without both sides clapping.",
    "G054": "Refraining from answering the provocative political taunt at the dinner table, Shridhar enjoyed a serene evening, realizing that while speech is silver, silence is pure gold.",
    "G055": "Though her puppy was muddy and had torn ears, the little girl hugged it fiercely and proclaimed it the prettiest pet in the district, just as every crow loves its chick.",
    "G056": "Now that the retired clerk finally had the money to tour snow-capped Himalayan peaks, his failing knees kept him indoors, illustrating having teeth without nuts and nuts without teeth.",
    "G057": "Looking around the crowded train compartment, the commuter realized that beneath polite smiles, every single person carried their own private weight of worries.",
    "G058": "Seeing the corrupt municipal contractor finally arrested for tax fraud, the townsfolk shook their heads, knowing that in the cosmic order, each soul reaps its own karma.",
    "G059": "Once the cruel rumor slipped from her tongue in the tea party, no tearful apology could undo the heartbreak it caused, just like a shattered pearl that cannot be remade.",
    "G060": "Despite three corporate ethics workshops, the dishonest cashier was caught skimming five-rupee coins again, proving that a dog's tail remains hopelessly bent.",
    "G061": "Ignoring the fresh medicinal neem leaves growing in her backyard, Lakshmi bought expensive branded herbal pills from the pharmacy, forgetting that the backyard plant is never valued as medicine.",
    "G062": "With the father wanting to sell the farmland, the mother wanting to lease it, and the son wanting to build a warehouse, their household became a house with three conflicting doors.",
    "G063": "Accepting that his elder child excelled in music while the younger loved wrestling, the father smiled, knowing that all fruits grown on the same branch do not share identical sweetness.",
    "G064": "The moment the hostel warden mentioned that someone had snuck into the pantry, the guilty boy involuntarily wiped chocolate syrup from his sleeve, like the pumpkin thief feeling his shoulder.",
    "G065": "Spending lavishly to sponsor the village cricket tournament while his own aged mother starved without medication, the hypocrite was mocked as a plague at home and an angel to the town.",
    "G066": "Dressed in crisp silks for the temple festival, the quiet family hid the agony of their daughter's prolonged hospital illness, for inner domestic turmoil rarely shows outside.",
    "G067": "A gentle, respectful conversation initiated by the grandmother over morning coffee smoothed months of silence between the sisters-in-law, uniting a fractured household.",
    "G068": "Listening carefully to the retired blacksmith's technique for tempering iron saved the apprentice years of trial and error, proving elder counsel rings like a pure brass bell.",
    "G069": "Running barefoot across the veranda with joyous laughter, the twin toddlers brought light and warmth into their grandparents' quiet house, serving as the true eyes of the home.",
    "G070": "Long before he stepped into a formal classroom, the boy learned honesty and compassion from his grandmother's bedtime stories, showing that home is the foundational school.",
    "G071": "After eating lavish banquets across foreign hotels, the homesick student craved his mother's simple rasam, affirming that there is no kin like a mother and no flavor like salt.",
    "G072": "Checking the bridegroom's family reputation and the soil quality before leasing the farm, the cautious elder advised inspecting the household before giving one's daughter.",
    "G073": "Though living under one tiled roof, the four brothers held wildly different ambitions, showing that one house can hold a hundred distinct minds.",
    "G074": "Visiting the ancestral village felt warm and welcoming only so long as the elderly matriarch sat on the porch, for where a mother lives, the maternal sanctuary endures.",
    "G075": "With her gentle speech, selfless service, and integrity, the elder daughter brought honor and peace to both families, like a sacred lamp illuminating the entire home.",

    # G076 - G100
    "G076": "Putting aside petty grievances and celebrating festivals together turned their cramped dwelling into a heaven, confirming that unity makes any home celestial.",
    "G077": "Rather than humiliating his childhood buddy to win a heated debate on cricket statistics, Vinay conceded gracefully, knowing that preserving friendship matters more than winning an argument.",
    "G078": "What began as a petty dispute over parking space between two brothers ended up being broadcast across the entire colony, proving that domestic quarrels soon become public spectacles.",
    "G079": "Seeking solace after a bruising corporate career, the tired man sat beside his elderly mother and rested his head in her lap, finding the purest temple on earth.",
    "G080": "When the neighborhood shopkeepers banded together against the local extortion gang, the troublemakers fled, proving that collective unity multiplies human strength.",
    "G081": "Loudly condemning his colleague for taking a ten-minute tea break while ignoring his own hours of online shopping, the supervisor saw the grass blade in another's eye but missed the log in his own.",
    "G082": "Quick to point out spelling typos in other students' assignments, the arrogant boy never noticed his own total lack of mathematical logic, blind to his personal shortcomings.",
    "G083": "Throwing his laptop against the brick wall in a blinding flash of fury left him with broken equipment and a cancelled contract, learning that a nose cut in anger cannot be restored in peace.",
    "G084": "A single reckless insult hurled during the wedding luncheon divided two branches of the family for thirty years, proving that careless words destroy homes just as leaks ruin stoves.",
    "G085": "Negotiating a peaceful land settlement where neither farmer lost acreage nor took the dispute to court, the village headman resolved the issue so the snake died without breaking the stick.",
    "G087": "Offering a polite greeting and listening patiently to the frustrated tenant transformed an angry confrontation into a warm mutual agreement, proving that kind words build lasting bonds.",
    "G088": "Though external rivals attempted to undercut their family business, the three sisters stood shoulder-to-shoulder, showing that internal unity is the greatest fortress.",
    "G089": "Taking turns watching each other's cattle and sharing agricultural tractors during harvest season made life manageable and sweet for the dryland farmers.",
    "G090": "Demanding a commission before recommending his closest friend for an open job opening poisoned their decades of brotherhood, proving that selfish greed must never intrude upon friendship.",
    "G091": "By returning the borrowed gold ornaments promptly on the promised morning without a scratch, Sunita preserved the priceless trust that held her extended family together.",
    "G092": "When his wife suddenly went into labor at midnight during a downpour, it was the next-door neighbor who drove them to the clinic, proving a good neighbor is better than distant kin.",
    "G093": "Instead of retaliating against his roommate's annoying habits, Praveen addressed the matter gently over dinner, using patience as a sturdy bridge across differences.",
    "G094": "Winning the stubborn stray dog's trust with a bowl of warm rice achieved in five minutes what shouting and brandishing sticks could never accomplish.",
    "G095": "Though he wore tailored suits and gold watches, the man's arrogant dismissals of the canteen waiter revealed his true, uncultured character.",
    "G096": "Greeting both the senior director and the office janitor with identical warmth, the young executive established that mutual respect forms the bedrock of all human ties.",
    "G097": "Sitting beside him in the hospital waiting room through the bleakest hours of the night, Chetan showed that the one who stands with you in grief is your genuine companion.",
    "G098": "Honoring his verbal commitment to deliver the handloom sarees despite raw silk prices doubling overnight, the honest weaver proved that a pledged word must always be kept.",
    "G099": "He possessed neither vast real estate nor offshore shares, yet surrounded by loving grandchildren and loyal neighbors, the retired teacher lived as the richest man in the town.",
    "G100": "Stepping quietly to cover the night shift for a tired colleague whose child had a high fever, the nurse showed that true humanity lies in understanding another's pain.",
    "G101": "Failing her dance audition and immediately complaining that the stage wooden floor was tilted, the conceited girl illustrated the inept dancer blaming the uneven ground.",

    # G102 - G125
    "G102": "Trying to explain quantum cryptography to an uncle who insisted smartphones are possessed by spirits felt like playing a divine lute before a buffalo.",
    "G103": "Handing an antique leather-bound Sanskrit manuscript to an unruly toddler who used it as coloring scrap was truly giving a priceless ruby into a monkey's paw.",
    "G104": "Throwing gourmet artisanal French cheese to an unruly street hound that preferred discarded bone scraps showed that a donkey has no appreciation for the fragrance of musk.",
    "G105": "Offering a pair of high-powered binoculars to someone who refused to open his eyes was as meaningless as holding up a mirror before a blind man.",
    "G106": "Remaining silent would have kept everyone assuming he was an expert, but the moment he opened his mouth and misquoted basic geography, his ignorance was on display.",
    "G107": "After reading two unverified health blog posts, the amateur self-prescribed heavy antibiotics and ended up in the emergency ward, proving half-baked knowledge is perilous.",
    "G108": "When unsure about operating the high-voltage lathe, the apprentice asked the senior mechanic, respecting the rule that the uninformed must ask and the knowledgeable must guide.",
    "G109": "Endlessly gossiping about everyone's private affairs at the residential society meeting created bitter factions, proving that excess chatter ruins peaceful homes.",
    "G110": "Though the tongue has no bone of its own, the cruel remarks it utters can shatter the strongest bones and spirits; words carry weight and consequence.",
    "G111": "Bringing up ancient property rivalries in the middle of a delicate wedding negotiation was like pouring pure ghee directly into a raging campfire.",
    "G112": "Falsifying his first test score forced the student to invent a fake sickness, forge a doctor's slip, and dodge phone calls, demonstrating that one lie demands a hundred more.",
    "G113": "Giving sensible financial advice to a spendthrift who ignored every warning was as fruitless as blowing a sacred conch into a brass ear.",
    "G114": "While other candidates posted theatrical campaign videos online, the quiet social worker repaired three village wells, living the maxim of speaking less and doing more.",
    "G115": "Weighing each sentence before addressing the agitated crowd, the elder spoke with gentle grace, ensuring his words fell like soothing pearls.",
    "G116": "An uncontrolled urge to share confidential company gossip over drinks cost the senior manager his prestigious career, proving loose lips ruin lives.",
    "G118": "Every time the police cruiser passed through the market lane, the shopkeeper who kept stolen watches nervously twitched his collar, displaying a thief's restless mind.",
    "G119": "Whenever called upon to help clean the neighborhood drainage ditch, the chronic shirker had a convenient headache, showing a dishonest person always finds an excuse.",
    "G120": "By recklessly vandalizing the shared community water pipeline after his personal connection was cut, the disgruntled youth ruined the entire orchard for everyone.",
    "G121": "Placing an uncultivated, boorish fellow in a regal palace surrounded by classical art brings no joy to him; to an ignorant mind, even a palace feels like an alien forest.",
    "G122": "Quick to lecture his colleagues on punctuality, the supervisor never realized he spent two hours daily playing games, incapable of inspecting his own back.",
    "G123": "When chaos and yelling broke out during the disorganized society meeting, the pragmatic member quietly helped himself to the buffet samosas and walked away satisfied.",
    "G124": "When his in-laws began trading angry accusations over festival gifts, Srinivas folded his hands and held his peace, knowing silence is the only remedy in a house of noise.",
    "G126": "Do not be swayed by the smooth-talking salesman's grand promises of instant wealth; examine the actual product performance and value concrete deeds.",
    "G127": "Deceived by the fraudster's aristocratic attire and charming smile, the investor handed over his money, regretting judging character solely by outward appearance.",
    "G128": "The glitzy showroom looked prosperous from the highway, but closer inspection revealed massive unpaid supplier debts, proving not everything visible to the eye is true.",

    # G129 - G155
    "G129": "The gold-plated wrist watch bought from the pavement vendor tarnished into dull green copper within three days, reminding the buyer that all that glitters is not gold.",
    "G130": "Beneath the polished marble facade and velvet couches of the coaching academy lay incompetent tutors and outdated notes, golden on the outside but stone within.",
    "G132": "The noisy politician who shouted the loudest during the rally had never sponsored a single development project, acting like an empty vessel that clatters loudest.",
    "G133": "Boasting that his tech startup was invincible and mocking his competitors, the arrogant CEO went bankrupt within two quarters, proving pride precedes downfall.",
    "G134": "Appointing an impulsive, vindictive teenager as the group administrator resulted in half the members being blocked in anger, like handing a sharp blade to a monkey.",
    "G136": "To someone who has never appreciated architecture, the historic temple tower appears as nothing more than a pile of carved granite blocks.",
    "G137": "When the young apprentice showed genuine curiosity and eagerness to learn, the master woodcarver gladly revealed his secret carving techniques, for a listening ear finds a speaking mouth.",
    "G138": "Once his embezzlement was exposed to his business partners, no amount of collateral could restore his credit, for losing trust is losing everything.",
    "G139": "After pulling three fake panic alarms just to watch the staff scramble, the boy found no one responding when a real kitchen grease fire erupted, like the boy who cried wolf.",
    "G140": "Waiting nervously for the auditor's report, the corrupt clerk couldn't sit still and kept pacing the corridor, for a thief's feet can never rest steady on the ground.",
    "G141": "A single vulgar comment posted on the company's official forum tarnished months of good marketing, showing that one drop of poison spoils a cauldron of milk.",
    "G142": "Having suffered severe food poisoning from street mayonnaise last monsoon, the girl became cautious of even eating a plain cold salad, like a scalded kitten fearing every cat.",
    "G143": "While reckless gullibility is foolish, closing one's heart to all human trust leaves a person utterly isolated; genuine faith is essential for a meaningful life.",
    "G144": "Though powerful enemies attempted to bury the truth under fabricated police reports, the innocent man was finally exonerated, proving truth never dies.",
    "G145": "Despite enduring years of legal hurdles and intimidation, the whistleblowing engineer stood firm until the bridge contractor was prosecuted, confirming truth ultimately triumphs.",
    "G146": "Listening to the candidate treat his campaign staff with genuine courtesy convinced the voters of his noble character, for words are the mirror of the human heart.",
    "G147": "When his calculation error caused a system crash, the senior developer stood up in the meeting and took full responsibility, showing that admitting a mistake is true greatness.",
    "G148": "Having once lost his down payment to an unregistered real estate builder, the wise buyer thoroughly inspected municipal approvals the second time, learning from experience.",
    "G149": "Instead of inventing defensive excuses for the botched presentation, the young intern redrafted the slides and asked for feedback, demonstrating that mistakes should be rectified.",
    "G150": "No university lecture could teach him the unpredictable nature of agricultural seasons as thoroughly as three decades of farming his own land, for experience is the greatest guru.",
    "G151": "Watching the town councilors rush to greet the wealthy liquor baron while ignoring the retired school headmaster showed that in this mundane world, money remains king.",
    "G152": "Taking on massive high-interest credit card debt just to dine at five-star rooftop lounges is the height of folly; never borrow money to eat clarified butter.",
    "G153": "When a man has millions in his bank account, even sleeping on a simple coarse blanket is praised by flatterers as profound philosophical simplicity.",
    "G154": "Seeing how quickly bureaucratic obstacles melted away once the builder handed over grease money, the onlookers remarked that cash makes even a corpse open its jaws.",
    "G155": "Carrying an empty wallet while swaggering through the bazaar and bragging about ancestral estates made the foolish youth an object of town ridicule.",

    # G156 - G185
    "G156": "Wearing imported designer sunglasses while his younger siblings begged for basic school fees illustrated having no grain in the belly but jasmine flowers in the hair.",
    "G157": "The lazy student expected an A-grade on the group project without contributing a single paragraph of research, craving the feast while detesting the labor.",
    "G158": "With sufficient emergency savings tucked away in fixed deposits, the family handled the sudden hospital surgery smoothly, proving that having money softens many blows.",
    "G159": "The kind man who lent money was treated like a fool while the shameless borrower lived extravagantly and refused to repay, turning the lender into a clown.",
    "G160": "Stealing a handful of betel nuts ruined the merchant's thirty years of honesty in the village market, proving that respect lost over a trifle cannot be bought back with an elephant.",
    "G161": "The deceitful trader made quick profits for a month before his warehouse was raided, whereas the honest merchant across the street prospered for fifty years.",
    "G162": "The con artist who tricked elderly pensioners with fraudulent land deeds was eventually swindled of all his ill-gotten wealth by his own business partner.",
    "G165": "When the corrupt inspector was finally suspended from duty and faced judicial inquiry, nobody was surprised, knowing that whoever eats salt must drink water.",
    "G166": "Though the company spokesperson denied any takeover rumors, the presence of five international auditors in the conference room showed there is no smoke without fire.",
    "G167": "Knowing his books were clean, the honest accountant welcomed the government audit with a relaxed smile, for truth bestows courage while dishonesty breeds terror.",
    "G171": "Matching his family's modest holiday trip to their actual monthly savings prevented any debt, exemplifying tying anklets that match the size of one's ankles.",
    "G172": "Booking a victory party banquet two weeks before the election ballots were even cast made the overconfident politician a laughingstock when results were announced.",
    "G173": "Just as the student reached out to sign the scholarship acceptance papers, the funding council announced an indefinite budget freeze, losing the morsel before it reached the mouth.",
    "G175": "Bailing out the ungrateful relative who immediately badmouthed him behind his back felt exactly like pouring warm milk down a venomous serpent's throat.",
    "G176": "While the wealthy landlord sat on his veranda laughing at the dog chasing the stray goat, the impoverished goat owner wept over his livelihood, showing one's sport is another's agony.",
    "G178": "Seeing the stone-faced clerk suddenly smile and process the file within minutes of seeing the envelope proved that money makes even corpses speak.",
    "G185": "When the veteran industrialist launched his new venture, smaller suppliers and investors immediately followed his footsteps, for wherever the mighty elephant walks, a path is made.",
    "G186": "The senior clerk who was once bullied by his manager became a gentle, supportive supervisor himself, knowing that every mother-in-law has her day and every daughter-in-law has hers.",
    "G187": "The sudden power blackout happening right as the cat jumped on the fence was pure coincidence; a crow perching on a bough does not prove it snapped the timber.",
    "G188": "When the stolen laptop was found right inside the suspect's backpack, there was no need for further investigation, for why hold a mirror to view a blister on one's own palm?",
    "G189": "Speaking up clearly about her unfair workload during the annual review got her assigned two assistants, proving that only the crying child receives milk.",
    "G191": "Eating balanced home-cooked meals kept the old farmer free of illness, while speaking gently kept him free of lawsuits, proving mindful diet and speech prevent trouble.",
    "G192": "Managing the kitchen and family pantry with exceptional thrift and culinary flair made the young bride the respected mistress of the entire household.",
    "G194": "Once the Supreme Court issued its final verdict on the river water dispute, both states had to comply, for an authoritative decree is etched in granite.",
    "G201": "Though thieves could rob his cattle and fire could destroy his barn, the scholar's deep knowledge remained untouched, proving education is the only imperishable wealth.",

    # G202 - G226
    "G202": "Even after losing his job during the economic downturn, the skilled carpenter started a custom furniture business and thrived, for learning acquired never abandons the hand.",
    "G203": "Following the rigorous problem-solving approach taught by his high school mathematics mentor helped the scientist solve complex rocket equations, guided by his teacher's path.",
    "G204": "Spending quiet evenings immersed in classic literature illuminated the young girl's mind, proving the friendship of books brings true light to human life.",
    "G205": "Despite holding two doctorates from world-renowned universities, Dr. Rao spoke humbly to every hospital orderly, illustrating that humility is the supreme ornament of education.",
    "G206": "Working the rich black soil with compost and diligent weeding rewarded the farmer with towering maize stalks, showing that land tilled with devotion never betrays.",
    "G207": "Sleeping under the cool shade of the banyan tree during the crucial monsoon sowing weeks left the lazy farmer weeping before an empty barn during harvest time.",
    "G208": "Testing the soil moisture and adjusting crop rotation according to the land's texture proved that understanding the earth is the hallmark of a master farmer.",
    "G209": "Whatever technological revolutions sweep through our cities, agriculture remains the indispensable backbone sustaining all human existence.",
    "G210": "A barren, neglected acre gains true value only when green shoots of ragi push through the dark soil, for land's true worth is proven through its harvest.",
    "G211": "By planting two hundred native banyan and tamarind saplings along the canal bunds, the village retained its groundwater, knowing trees preserve rain.",
    "G212": "Protecting the sprawling forest canopy around the valley ensured clean mountain springs and fresh air, proving that where greenery thrives, life breathes.",
    "G213": "Conserving every droplet of rain in recharge wells sustained the arid community through summer, honoring water as the very foundation of life.",
    "G214": "Desilting the ancient riverbanks and refusing to dump plastic into the stream protected the valley from flash floods, showing nature protects those who protect her.",
    "G215": "When the rejuvenated village lake brimmed with crystal water after the rains, both the agricultural wells and the cattle thrived, blessing the entire community.",
    "G216": "Recovering from severe burnout taught the corporate executive to prioritize sleep and daily exercise, realizing that good health is the greatest wealth.",
    "G217": "Eating half a belly of fresh food and drinking warm water kept the grandmother energetic at eighty, demonstrating that measured eating is the secret of vitality.",
    "G218": "Avoiding overly oily, processed snacks and dining with mindfulness allowed the professor to maintain vibrant health and peace of mind.",
    "G219": "Eating modest, wholesome portions and leaving the dinner table lightly satisfied treats food as divine nectar rather than a burden on the stomach.",
    "G220": "Washing hands thoroughly and keeping the water storage vessels covered prevented all seasonal fevers in the school, proving cleanliness is the first step to health.",
    "G221": "By always replacing defective goods without arguing and keeping his prices fair, the fabric merchant built an empire of trust, the true capital of trade.",
    "G222": "Failing to maintain a daily ledger of shop expenses and credit sales led the grocery store into sudden bankruptcy, proving accounting is vital to commerce.",
    "G223": "Greeting even the most demanding shopper with patience and a welcoming smile, the shopkeeper prospered, honoring the customer as the deity of commerce.",
    "G224": "Instead of chasing speculative windfalls, the bakery owner banked steady small profits each month, slowly building a chain of three successful outlets.",
    "G225": "A single rupee earned by honest sweat carries greater peace of mind and dignity than thousands acquired through deceit or inheritance.",
    "G226": "When the youth volunteered to repair the damaged municipal culvert, the whole village prospered, proving the community's welfare is everyone's welfare.",

    # G227 - G252
    "G227": "Distributing warm blankets and hot porridge to stranded migrants during the cold winter night was a noble act of selfless compassion.",
    "G228": "Living beside considerate neighbors who checked on her elderly parents every afternoon gave the working doctor tremendous peace of mind, a true life asset.",
    "G229": "No single family could build the village grain storage unit alone; it was mutual cooperation and shared labor that made communal life thrive.",
    "G230": "Sharing the bowl of sweet payasa with the neighboring children brought ten times more happiness than eating the entire pot alone.",
    "G231": "By leading with composure, empathy, and clear instructions during the crisis, the captain inspired his team to victory, proving leadership shapes team strength.",
    "G232": "Taking the first step into the flooded road to guide the trapped bus passengers to safety, the local youth showed that whoever claims leadership must demonstrate the way.",
    "G233": "Sitting in the magistrate's chair, the judge remembered that the power to punish is secondary to the grave responsibility to dispense impartial justice.",
    "G234": "Resolving boundary disputes fairly without taking bribes or favoring relatives earned the village elders enduring respect and community trust.",
    "G235": "Transparent municipal accounting, paved roads, and prompt drinking water supply brought prosperity to the district, proving good administration is a people's blessing.",
    "G236": "Confronting his stutter and stepping onto the debate podium with a steady heart, the young student discovered that courage illuminates the darkest path.",
    "G237": "Paralyzed by the fear of being rejected, the timid applicant never submitted his proposal, proving that those who fear can never seize opportunities.",
    "G238": "Viewing his business bankruptcy not as a final defeat but as a priceless lesson, the entrepreneur built a resilient logistics firm, using challenges as stepping stones.",
    "G239": "After tumbling off the bicycle five times and scraping his knees, the boy got back on the pedals and mastered balance, for only he who falls learns to rise.",
    "G240": "Refusing to despair even when his field trial failed three times, the agricultural scientist pressed on until his drought-resistant seed variety flourished.",
    "G241": "No diamond necklace or silk attire could match the dignity radiated by the modest teacher who treated every human being with gentle courtesy and noble values.",
    "G242": "Teaching his children to read, speak, and write beautiful Kannada while living in Chicago preserved their cultural heritage across generations.",
    "G243": "Consulting his eighty-year-old grandfather before laying the foundation for the ancestral house saved the young architect from digging into underground springs.",
    "G244": "Lighting brass lamps at dusk and singing devotional vachanas connected the modern family to centuries of living tradition, rooted deep in culture.",
    "G245": "No foreign poetry could evoke the raw emotional resonance and sweetness that a simple lullaby sung in one's mother tongue stirs in the heart.",
    "G246": "Waking up at five each morning for disciplined music practice enabled the violinist to master difficult ragas, confirming discipline breeds excellence.",
    "G247": "Arriving ten minutes before the scheduled interview impressed the board before a single question was asked, showing punctuality is the first step to achievement.",
    "G248": "Carefully verifying and delivering the small daily postal parcel built the courier's reputation, showing handling small tasks reliably earns profound trust.",
    "G249": "Following traffic regulations and wearing a helmet kept the commuter safe throughout years of chaotic city transit, proving rules safeguard peace.",
    "G250": "Instead of leaving the leaky tap repair for the weekend, the prudent homeowner tightened the washer immediately, completing today's duty today.",
    "G251": "Scrambling to purchase emergency water storage drums only after the municipal borewell had run completely dry felt like digging a well after the house caught fire.",
    "G252": "Hearing her neighbor lament about domestic quarrels, Sunita smiled gently and comforted her, reminding her that every house's dosa has its hidden holes."
}


def populate_examples():
    print("=== POPULATING TEAM-DRAFTED EXAMPLES IN GAADES.CSV ===")
    
    # 1. Read existing gaades.csv
    with open(GAADES_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"Loaded {len(rows)} rows from gaades.csv")
    
    # Verify all canonical gaade_ids have an example
    csv_ids = [r["gaade_id"] for r in rows]
    missing = set(csv_ids) - set(EXAMPLES.keys())
    if missing:
        raise ValueError(f"Missing examples for gaade IDs: {missing}")

    # Check for empty examples or formatting
    filled_count = 0
    for r in rows:
        gid = r["gaade_id"]
        ex = EXAMPLES[gid].strip()
        if not ex:
            raise ValueError(f"Empty example generated for {gid}")
        r["example"] = ex
        filled_count += 1

    # Write back gaades.csv preserving all fields and exact Kannada text
    with open(GAADES_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[✓] Successfully populated {filled_count} examples into gaades.csv")

    # 2. Update gaade_provenance.csv with example_source column
    print("\n=== UPDATING GAADE_PROVENANCE.CSV WITH EXAMPLE_SOURCE ===")
    with open(PROVENANCE_CSV, "r", encoding="utf-8") as f:
        prov_reader = csv.DictReader(f)
        prov_fieldnames = list(prov_reader.fieldnames)
        if "example_source" not in prov_fieldnames:
            prov_fieldnames.append("example_source")
        prov_rows = list(prov_reader)

    prov_updated = 0
    for prow in prov_rows:
        gid = prow["gaade_id"]
        # Mark as team_drafted for canonical rows we filled
        if gid in EXAMPLES:
            prow["example_source"] = "team_drafted"
            prov_updated += 1
        else:
            prow["example_source"] = "team_drafted"  # Also mark duplicates as team_drafted
            prov_updated += 1

    with open(PROVENANCE_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=prov_fieldnames)
        writer.writeheader()
        writer.writerows(prov_rows)

    print(f"[✓] Successfully updated {prov_updated} rows in gaade_provenance.csv (example_source='team_drafted')")

    # 3. Reload SQLite database
    print("\n=== RELOADING SQLITE DATABASE WITH NEW EXAMPLES ===")
    import sys
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from scripts.load_db import load_data
    load_data()
    print("[✓] SQLite database reloaded successfully.")


if __name__ == "__main__":
    populate_examples()

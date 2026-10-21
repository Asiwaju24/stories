"""Set up genres and sample stories for the kids and adults sections.

    python manage.py seed_stories

Safe to run more than once. It only replaces a story's text while it is still
the short placeholder, and it never prints or sets any password.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from stories.models import Genre, Story

GENRES = [
    # slug, name, audience, emoji
    ('romance', 'Romance', Genre.ADULTS, '💕'),
    ('horror', 'Horror', Genre.ADULTS, '👻'),
    ('drama', 'Drama', Genre.ADULTS, '🎭'),
    ('mystery', 'Mystery', Genre.ADULTS, '🔍'),
    ('adventure', 'Adventure', Genre.BOTH, '🧭'),
    ('fantasy', 'Fantasy', Genre.BOTH, '🐉'),
    ('science-fiction', 'Science Fiction', Genre.BOTH, '🚀'),
    ('bedtime', 'Bedtime', Genre.KIDS, '🌙'),
    ('animals', 'Animal Tales', Genre.KIDS, '🦊'),
    ('fairy-tales', 'Fairy Tales', Genre.KIDS, '🧚'),
]

# Full versions of the six one-line placeholder stories. Each keeps the original
# opening sentence. They are only applied while a story's text is still the short
# placeholder (under 300 characters), so anything you have edited is left alone.
REWRITES = {
    'love-under-the-stars': {
        'audience': Story.ADULTS, 'content_warning': 'Romantic themes',
        'content': (
            "On a warm summer night, Emma met Liam under the glowing stars. She had come to the "
            "rooftop of the old cinema only because her sister insisted, and because a free "
            "outdoor screening of a film she had already seen four times sounded better than "
            "another evening alone with her spreadsheets.\n\n"
            "He was on his knees beside the projector, tightening something with a butter knife. "
            "He did not work there, she soon learned. He just could not stand to watch it flicker.\n\n"
            "\"You're going to electrocute yourself,\" she said.\n\n"
            "\"Probably,\" he agreed, without looking up. \"But the picture will be sharp.\"\n\n"
            "It was. When the film began, the whole rooftop went quiet, and Emma realised she was "
            "smiling at the screen for the first time in months. Her divorce had been final for "
            "eleven weeks. She had stopped counting days and started counting weeks, which her "
            "sister said was progress.\n\n"
            "At the interval Liam handed her a paper cup of lukewarm tea from a flask. They talked "
            "about nothing: the heat, the terrible seats, the way the lead actor always "
            "looked slightly surprised to be loved. He told her he taught maths to teenagers and "
            "was terrible at small talk. She told him she was an accountant and was, for once, "
            "enjoying it.\n\n"
            "When the credits rolled, nobody moved. The stars had come out properly by then, more "
            "than she ever saw from her flat, and Liam pointed out three constellations, getting "
            "one of them wrong on purpose just to see if she would notice. She did.\n\n"
            "They did not kiss. She was not ready, and he seemed to know it. He wrote his number "
            "on the back of the cinema flyer, then crossed it out and wrote it again, more "
            "neatly.\n\n"
            "\"No pressure,\" he said. \"But I fix projectors on Fridays.\"\n\n"
            "Emma folded the flyer into her pocket and walked home under the same stars, in no "
            "hurry at all. On Friday she was back on the roof."
        ),
    },
    'into-the-unknown': {
        'audience': Story.KIDS, 'age_group': '9-12',
        'moral': 'Respect the people who know the land, and prepare before you set out.',
        'content': (
            "James packed his bag, leaving behind the city to explore the Amazon rainforest. "
            "He had spent two years saving for the trip and six months reading about it, and he "
            "was certain he was ready.\n\n"
            "On the first morning his guide, a quiet woman called Marisol, looked at his bag and "
            "shook her head. \"Too heavy,\" she said. She took out his three spare shirts, his "
            "giant torch and a book of poems, and left him a water filter, a rain jacket and "
            "dry socks. \"The forest does not care what you brought. It cares what you can carry.\"\n\n"
            "They walked for six hours through air as thick as a wet towel. Marisol stopped "
            "often, tilting her head. James heard only insects. She heard everything: a troop of "
            "monkeys far ahead, a river somewhere to the east, and a sound he missed completely, "
            "the low creak of a branch about to fall. She pulled him back a second before it "
            "crashed across the path.\n\n"
            "That night they hung hammocks under a plastic roof while rain hammered down. James, "
            "who had been proud and a little cross all day, finally asked, \"How did you hear it?\"\n\n"
            "\"I listen more than I talk,\" she said, and smiled. \"It takes years. You can start "
            "tonight.\"\n\n"
            "So he did. He lay in the dark and sorted the sounds: frogs, rain, a distant "
            "bird that sounded like a squeaky door. By the end of the week he could tell which "
            "plants were safe to touch and which were not, and he had stopped checking his "
            "phone, which had no signal anyway.\n\n"
            "On the last morning the clouds lifted and a blue-and-gold macaw landed on a branch "
            "above him, close enough to count its feathers. James did not reach for his camera. "
            "He just watched, quietly, the way Marisol had taught him."
        ),
    },
    'the-haunted-manor': {
        'audience': Story.ADULTS, 'content_warning': 'Fear, mild peril',
        'content': (
            "Nobody dared to enter the old Greywood Manor... until I did.\n\n"
            "I should explain that I am not brave. I am a surveyor. The council had condemned the "
            "building and paid me to measure it before the demolition crew arrived on Monday. It "
            "was a Friday afternoon in October, the light already going, and I told myself it was "
            "a job like any other.\n\n"
            "The front door was not locked. That bothered me more than if it had been.\n\n"
            "Inside, the air was cold in a way that had nothing to do with the weather. I worked "
            "through the ground floor with my laser measure, calling the numbers aloud into my "
            "recorder out of habit. Hall: six by nine. Drawing room: eight by eleven. I noticed "
            "the dust lay thick on every surface except the banister, which was clean, as if "
            "someone used it often.\n\n"
            "On the second floor, the recorder picked up something I had not said. When I played "
            "it back in the car later, there it was between my measurements: a woman's voice, "
            "soft and patient, saying \"Mind the third stair.\"\n\n"
            "I did not hear it then. I only knew that on the way down, with my arms full of "
            "equipment, my foot went through the third stair and the board splintered under me. "
            "I caught the rail, the clean rail, and found I was not afraid. I was grateful.\n\n"
            "I finished the survey by moonlight. When I locked up, there was a light in the attic "
            "window that I had not seen on the way in, a small steady glow, like a lamp left on "
            "for a late visitor.\n\n"
            "On Monday the demolition crew found the attic empty. No lamp, no wiring, no "
            "window even, only bricked-over space I had never been able to measure.\n\n"
            "I have kept the recording. I play it sometimes, and I never get past the third stair "
            "without a quiet thank you."
        ),
    },
    'the-dragons-secret': {
        'audience': Story.KIDS, 'age_group': '6-8',
        'moral': 'Real courage is being kind to someone who is afraid.',
        'content': (
            "In the kingdom of Eldoria, dragons were thought to be extinct. Everyone had heard the "
            "stories, but nobody had seen one for a hundred years.\n\n"
            "Wren, who was eight, did not believe the stories. She believed what she saw, and what "
            "she saw one rainy morning was a pair of green eyes glowing in the old well behind the "
            "bakery.\n\n"
            "\"Hello?\" she whispered.\n\n"
            "\"Please go away,\" said a very small voice. \"I am terrifying.\"\n\n"
            "Wren peered down. At the bottom, curled up on a pile of wet leaves, was a dragon no "
            "bigger than a goat. His scales were the colour of pond water and his wings were "
            "folded tight around him like an umbrella.\n\n"
            "\"You do not look terrifying,\" said Wren. \"You look cold.\"\n\n"
            "His name was Ember, though he said it was a silly name, because he could not make "
            "fire. Every time he tried, he only hiccuped. The other dragons had flown away to "
            "the mountains long ago and left him behind, and he had been too embarrassed to "
            "follow.\n\n"
            "Wren climbed down with a rope and a blanket. She did not laugh at him. She shared "
            "her warm bread roll instead, and Ember was so pleased that he hiccuped three times in "
            "a row.\n\n"
            "Out came a tiny puff of smoke. Then another. Then, on the fourth hiccup, a small, "
            "bright, perfect flame that lit up the whole well.\n\n"
            "\"I did it,\" he whispered. \"I did it because you were kind.\"\n\n"
            "From then on, Wren kept the secret. Every evening Ember lit the bakery oven for "
            "the baker, who never could work out why his bread had become the best in the "
            "kingdom. And on the coldest nights, a small green dragon curled up by the fire "
            "and hiccuped happily until morning."
        ),
    },
    'mars-chronicles': {
        'audience': Story.ADULTS, 'content_warning': 'Peril, loss of life',
        'content': (
            "The first human colony on Mars faced an unexpected threat. It was not aliens, or "
            "radiation, or even the dust storm that had been forecast for weeks. It was a "
            "single worn valve in the water recycler.\n\n"
            "Commander Adaeze Okoro found out at 3 a.m., when the alarm woke her and the colony "
            "display showed seventy-two hours of drinking water for forty-one people. The "
            "supply ship was nine months away.\n\n"
            "She called everyone to the mess hall. Nobody shouted. She had chosen these people "
            "partly for that.\n\n"
            "\"We can ration,\" said the doctor, Tomás. \"Half rations stretches it to a week.\"\n\n"
            "\"And the valve?\" asked Priya, the engineer, who had not slept. \"We have no spare. "
            "The part is printed from a polymer we ran out of in March.\"\n\n"
            "Adaeze looked around the room and made herself breathe. Then she said what she'd "
            "been thinking for an hour. \"We have a hundred and ten kilos of packaging. Food "
            "wrappers, storage boxes, the lot, the same polymer. Priya, can you melt it down?\"\n\n"
            "It took two days. The first print cracked under pressure. The second leaked. "
            "On the third attempt, Priya sat beside the printer for eleven hours, adjusting the "
            "temperature by half a degree at a time, while the storm outside blotted out the "
            "sun and the colony drank from emergency tanks.\n\n"
            "When the valve finally held, nobody cheered. They just stood in the quiet and "
            "listened to the recycler hum. Tomás cried. Priya fell asleep where she sat.\n\n"
            "In her log that night, Adaeze wrote: \"Day 412. Crisis resolved. We are not heroes. "
            "We are forty-one people who refused to stop thinking.\" Then she deleted the "
            "second sentence, and wrote it again, because it was true."
        ),
    },
    'the-last-goodbye': {
        'audience': Story.ADULTS, 'content_warning': 'Grief, dementia, ageing',
        'content': (
            "Tears rolled down her cheeks as she waved him off one final time. The care-home "
            "van pulled away from the kerb with her father in the front seat, his good "
            "cardigan buttoned wrong, his hand lifted in a wave he did not seem to understand.\n\n"
            "Nkechi had told herself she would be strong. She had read the leaflets, "
            "attended the family meeting, and signed the forms with a steady hand. Her brother "
            "had flown in for two days and flown out again, saying he trusted her to do what was "
            "best. She had hated him for that, a little, and hated herself for hating him.\n\n"
            "Her father had been a headmaster for thirty-one years. He used to know the name of "
            "every pupil and the birthday of every teacher. Lately he asked her, twice an "
            "hour, whether she had found his keys. He had no keys. The house had been sold in "
            "the spring.\n\n"
            "That morning, packing his case, she found a box of old school reports he had kept "
            "for decades. On the top one, in his sharp blue handwriting, he had written about a "
            "boy who struggled with reading: \"Give him time. He will surprise you.\"\n\n"
            "She had read that line three times on the floor of his empty bedroom.\n\n"
            "At the care home she would visit on Sundays. She knew it. She also knew that "
            "someday he would look at her kindly and ask who she was, and that she would answer "
            "gently, as he would have: \"I'm Nkechi. I'm someone who loves you.\"\n\n"
            "The van turned the corner. She stayed on the pavement a long time after it was "
            "gone, holding the box of reports against her chest, and then went in to put the "
            "kettle on, because somebody had to, and tomorrow was another day to be gentle."
        ),
    },
}

SAMPLES = [
    {
        'slug': 'the-sleepy-lighthouse', 'title': 'The Sleepy Lighthouse', 'genre': 'bedtime',
        'audience': Story.KIDS, 'age_group': '3-5', 'featured': True,
        'moral': 'Everyone needs rest, and a good friend helps you find it.',
        'content': (
            "At the edge of the sea stood a little lighthouse named Lulu. Every night she "
            "shone her light so the boats could find their way home.\n\n"
            "One evening Lulu yawned. \"I am so sleepy,\" she whispered. But the boats were "
            "still out on the dark water.\n\n"
            "A small crab named Pip heard her. \"I will keep watch,\" said Pip, and he waved "
            "a tiny lantern from the rocks. The boats saw it and came safely home, one by one.\n\n"
            "Lulu closed her eyes. The waves hummed a lullaby. Goodnight, Lulu. Goodnight, Pip."
        ),
    },
    {
        'slug': 'milo-the-brave-little-fox', 'title': 'Milo the Brave Little Fox', 'genre': 'animals',
        'audience': Story.KIDS, 'age_group': '6-8', 'featured': True,
        'moral': 'Being brave does not mean you are not scared. It means you try anyway.',
        'content': (
            "Milo was the smallest fox in the forest, and he was afraid of the dark.\n\n"
            "One night his baby sister wandered out of the den. Milo's tummy felt wobbly, but "
            "he took a deep breath and stepped into the shadows.\n\n"
            "\"Who is there?\" he called. An owl blinked down from a branch. \"Follow the "
            "fireflies,\" she hooted.\n\n"
            "Milo followed the tiny lights over the log, past the stream, and there was his "
            "sister, giggling at the glowing bugs. He hugged her tight and carried her home.\n\n"
            "The dark did not seem so big after that."
        ),
    },
    {
        'slug': 'the-map-in-the-attic', 'title': 'The Map in the Attic', 'genre': 'adventure',
        'audience': Story.KIDS, 'age_group': '9-12',
        'moral': 'The best treasures are the ones you find together.',
        'content': (
            "Zara and her cousin Tobi were sorting boxes in Grandpa's attic when a yellowed "
            "map slid out of an old atlas. A red cross marked a spot behind the garden wall.\n\n"
            "\"It has to be a joke,\" said Tobi. But they grabbed a spade and a torch anyway.\n\n"
            "Behind the wall, under a flat stone, they found a tin box. Inside were dozens of "
            "photographs, every one of Grandpa as a boy, laughing with his friends.\n\n"
            "Grandpa smiled when they showed him. \"I hid those so I would never forget how "
            "much fun we had,\" he said. That weekend he told them a story for every photo."
        ),
    },
    {
        'slug': 'the-princess-and-the-puddle', 'title': 'The Princess and the Puddle', 'genre': 'fairy-tales',
        'audience': Story.KIDS, 'age_group': '3-5',
        'moral': 'Kindness is the best crown.',
        'content': (
            "Princess Ada did not like to be clean. She liked to jump in puddles.\n\n"
            "One rainy day she found a frog stuck at the edge of the biggest puddle in the "
            "kingdom. Splash, splash, she scooped him up.\n\n"
            "\"Thank you,\" said the frog. \"I am the Frog Prince.\" But Ada only laughed. "
            "\"I do not need a prince. I need a puddle-jumping friend.\"\n\n"
            "So they jumped in puddles together every rainy day, and they were happy ever after."
        ),
    },
    {
        'slug': 'the-last-train-home', 'title': 'The Last Train Home', 'genre': 'drama',
        'audience': Story.ADULTS, 'featured': True,
        'content_warning': 'Grief, loss',
        'content': (
            "The platform was nearly empty when Ruth arrived, a suitcase in one hand and her "
            "mother's old umbrella in the other. Twenty years she had told herself she would "
            "come back for the funeral of someone who had never asked her to.\n\n"
            "The 11:40 was late. She sat on the cold bench and watched the board flicker, "
            "and for the first time in a long while she let herself remember the kitchen, "
            "the radio, the way her mother hummed while she burned the toast.\n\n"
            "When the train finally arrived, Ruth stood, hesitated, and then boarded. Not "
            "forgiven, exactly. But going home."
        ),
    },
    {
        'slug': 'the-clockmakers-ledger', 'title': "The Clockmaker's Ledger", 'genre': 'mystery',
        'audience': Story.ADULTS,
        'content_warning': 'Crime, mild violence',
        'content': (
            "Inspector Hale found the ledger wedged behind a grandfather clock that had "
            "stopped at 3:17. Every page was in the dead man's neat hand, except the last, "
            "which held a single line of numbers that did not belong to any account.\n\n"
            "It took her until dawn to see it: the numbers were not money. They were the "
            "times the shop's clocks had been wound, and only one person in town knew the "
            "route that visited them all in order.\n\n"
            "She closed the book, put on her coat, and went to pay the postman a visit."
        ),
    },
]


class Command(BaseCommand):
    help = 'Create genres and sample stories for the kids and adults sections.'

    def handle(self, *args, **options):
        User = get_user_model()
        author = User.objects.filter(is_superuser=True).order_by('id').first()

        genres = {}
        for slug, name, audience, emoji in GENRES:
            genre = Genre.objects.filter(slug=slug).first() or Genre.objects.filter(name=name).first()
            if genre is None:
                genre = Genre(slug=slug, name=name)
            genre.audience, genre.emoji = audience, emoji
            genre.save()
            genres[slug] = genre
        self.stdout.write(f'Genres ready: {len(genres)}')

        rewritten = 0
        for slug, data in REWRITES.items():
            story = Story.objects.filter(slug=slug).first()
            if story is None:
                continue
            if len(story.content.strip()) >= 300:
                continue  # already a real story, do not overwrite edits
            story.content = data['content']
            story.excerpt = ''  # regenerated from the new text on save
            story.audience = data['audience']
            story.age_group = data.get('age_group', '')
            story.moral = data.get('moral', '')
            story.content_warning = data.get('content_warning', '')
            story.save()
            rewritten += 1
        self.stdout.write(f'Placeholder stories rewritten in full: {rewritten}')

        created = 0
        for data in SAMPLES:
            data = dict(data)
            slug = data.pop('slug')
            genre = genres[data.pop('genre')]
            _, was_created = Story.objects.get_or_create(
                slug=slug,
                defaults={**data, 'genre': genre, 'author': author, 'status': Story.PUBLISHED},
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f'Sample stories created: {created}'))

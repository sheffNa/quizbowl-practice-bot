import discord
import docx2txt
import re
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter
import os
token = "NzM3MzQ1NzI3ODg5NjcwMjk2.Xx8AuA.6ZgFK64u8qe7YFK8ZoiqstUKjqc"
score1 = 0
score2 = 0
on_question = [0,0]
packet = ""
slowbowl_teamstates=["",""]
team1_answer = ""
team2_answer = ""
current_action = "inactive"
client = discord.Client()


@client.event
async def on_ready():
    print("Practice bot ready to roll!")
    await client.change_presence(status=discord.Status.idle)
    global current_action
    global score1
    global score2
    current_action = "waiting"
    score1 = 0
    score2 = 0
    print("waiting...")

@client.event
async def on_message(message):

    global current_action
    global on_question
    global score1
    global score2
    global packet
    global slowbowl_teamstates
    global team1_answer
    global team2_answer

    #prevent response to self
    if message.author == client.user:
        return

    #respond to messages beginning with "<"
    text = message.content.lower()
    if text[0] == "<":
        args = text.split()

        #handle entry into different modes
        if current_action == "waiting":

            #enter scorekeeping mode
            if args[0] == "<scorekeep":
                print("entering scorekeeping mode")
                score1 = 0
                score2 = 0
                await message.channel.send("Ok, beginning scorekeeping! Use \"<team1 x\" to add x points to team 1, \"<team2 x\" to add x points to team 2, and \"<end\" to end the game")
                current_action = "scorekeeping"
                await client.change_presence(status=discord.Status.online, activity=discord.Game(name="quizbowl (ok, not really, just keeping score - but i like to think it counts as playing!)"))

            #enter bonus mode
            elif args[0] == "<bonus":
                if len(args) == 1:
                    await message.channel.send("You haven't specified a packet, so I'll be reading from \"default\"")
                    packet = "default"
                else:
                    if os.path.isdir("packets/" + args[1]):
                        packet = args[1]
                        await message.channel.send("Found packet " + packet)
                    else:
                        await message.channel.send("No packet \"" + args[1] + "\" detected. To see all available packets, run \"<list\"")
                        return
                await message.channel.send("Alright, lets read some bonuses! To guess \"answer\", type \"<guess answer\", and to end the reading before the packet has been fully read, type \"<end\"")
                await client.change_presence(status=discord.Status.online, activity=discord.Game(name="bonuses"))
                current_action = "reading bonuses"
                print("entering bonus mode")
                #question 1, part 0
                on_question = [1, 0]
                await message.channel.send("---------------")
                f = open("packets/" + packet + "/bonuses/" + str(on_question[0]) + "/leadin", "r")
                text = f.read()
                f.close()
                await message.channel.send(text)
                f = open("packets/" + packet + "/bonuses/" + str(on_question[0]) + "/part" + str(on_question[1]), "r")
                text = f.read()
                f.close()
                await message.channel.send(text)



            #Prompt on partial command
            elif args[0] == "<slowbowl":
                await message.channel.send("Please use either \"<slowbowl_cooperative\" or \"<slowbowl_teams\"")

            #enter cooperative slowbowl mode
            elif args[0] == "<slowbowl_cooperative":
                if len(args) == 1:
                    await message.channel.send("You haven't specified a packet, so I'll be reading from \"default\"")
                    packet = "default"
                else:
                    if os.path.isdir("packets/" + args[1]):
                        packet = args[1]
                        await message.channel.send("Found packet " + packet)
                    else:
                        await message.channel.send("No packet \"" + args[1] + "\" detected. To see all available packets, run \"<list\".")
                        return
                score1 = 0
                score2 = 0
                for i in range(1, 21):
                    score2 += len(os.listdir("packets/" + packet + "/tossups/" + str(i)))
                await message.channel.send("To hear the next part, type \"<next\", to buzz \"answer\", type \"<guess answer\", and to end the reading before the packet has been fully read, type \"<end\". I will be keeping score for you against the packet. The maximum number of points possible in this packet are " + str(score2))
                await message.channel.send("You gain 2 points for getting a tossup right, plus 1 point for every clue remaining in the question after the point you get it. Count promptable answers as right unless you're pretty sure you wouldn't have converted it.")
                await client.change_presence(status=discord.Status.online, activity=discord.Game(name="slowbowl"))
                current_action = "cooperative slowbowl"
                print("entering cooperative slowbowl mode")
                await message.channel.send("---------------")
                #question 1, clue 0
                on_question = [1, 0]
                f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/clue" + str(on_question[1]), "r")
                text = f.read()
                f.close()
                await message.channel.send(text)

            #enter competitive slowbowl mode
            elif args[0] == "<slowbowl_teams" or args[0] == "<slowbowl_competitive":
                if len(args) == 1:
                    await message.channel.send("You haven't specified a packet, so I'll be reading from \"default\"")
                    packet = "default"
                else:
                    if os.path.isdir("packets/" + args[1]):
                        packet = args[1]
                        await message.channel.send("Found packet " + packet)
                    else:
                        await message.channel.send("No packet \"" + args[1] + "\" detected. To see all available packets, run \"<list\".")
                        return
                score1 = 0
                score2 = 0
                await message.channel.send("WELCOME TO THE COMPETITION OF THE CENTURY!!!!!!")
                await message.channel.send("TWO TEAMS HAVE GATHERED HERE TO DO BATTLE - A BATTLE OF WITS!")
                await message.channel.send("TWO TEAMS HAVE GATHERED - YET ONLY ONE CAN PREVAIL!")
                await message.channel.send("Further instructions will be sent to your individual team channels. Godspeed, noble adversaries! May the best team win!")
                await client.change_presence(status=discord.Status.online, activity=discord.Game(name="slowbowl"))
                current_action = "competitive slowbowl"
                print("entering competitive slowbowl mode")
                channel1 = discord.utils.get(message.channel.guild.text_channels, name="slowbowl-1")
                channel2 = discord.utils.get(message.channel.guild.text_channels, name="slowbowl-2")
                await channel1.send("Greetings, competitors. Your mission here is to completely destroy team 2. You may have known the people on team 2 once - you may even have considered them your friends. All that is gone. Now they are nothing but your opponents. They would obliterate you at the slightest hint of weakness, and so you must be prepared to do the same.")
                await channel2.send("Greetings, competitors. Your mission here is to completely destroy team 1. You may have known the people on team 1 once - you may even have considered them your friends. All that is gone. Now they are nothing but your opponents. They would obliterate you at the slightest hint of weakness, and so you must be prepared to do the same.")
                await channel1.send("The game works as follows: Both teams will be send a line of a tossup. The teams can take as long as they like to try and figure out the answer. They, they can either type \"<guess [answer]\" to submit the guess [answer] or \"<next\" to decline answering on that clue and wait for the next clue. Once both teams have made their decision, the game will proceed. If neither team has made a guess, both will be given the next part of the question and the process will continue. If one team has guessed correctly and the other has not, that team will get 2 points. If one team has guessed incorrectly, they will get 0 points and the other team will get 2 points. If both teams guess right, they both get 1 point, and if both guess wrong they both get 0 points. If one team cannot continue the game, they can type \"<surrender\" to end the game. Propmts are by default counted as incorrect, unless in your answer you specified \"guess [answer], [second_answer] if prompted\"")
                await channel2.send("The game works as follows: Both teams will be send a line of a tossup. The teams can take as long as they like to try and figure out the answer. They, they can either type \"<guess [answer]\" to submit the guess [answer] or \"<next\" to decline answering on that clue and wait for the next clue. Once both teams have made their decision, the game will proceed. If neither team has made a guess, both will be given the next part of the question and the process will continue. If one team has guessed correctly and the other has not, that team will get 2 points. If one team has guessed incorrectly, they will get 0 points and the other team will get 2 points. If both teams guess right, they both get 1 point, and if both guess wrong they both get 0 points. If one team cannot continue the game, they can type \"<surrender\" to end the game. Propmts are by default counted as incorrect, unless in your answer you specified \"guess [answer], [second_answer] if prompted\"")
                await channel1.send("We begin!")
                await channel2.send("We begin!")
                on_question = [1, 0]
                slowbowl_teamstates = ["waiting", "waiting"]
                f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/clue" + str(on_question[1]), "r")
                text = f.read()
                f.close()
                await channel1.send(text)
                await channel2.send(text)

            #list all uploaded packets
            elif args[0] == "<list":
                await message.channel.send("------packet list------")
                for packet in os.listdir("packets"):
                    await message.channel.send(packet)
                await message.channel.send("------end of list------")

            #enter process mode
            elif args[0] == "<process":
                #Ensure that the person issuing the command has been designated as trustworthy. This can be a dangerous command to let anyone use.
                trusted = 0
                for role in message.author.roles:
                    if role.name == "trusted uploader":
                        trusted = 1
                if not trusted:
                    print("access denied")
                    await message.channel.send("Sorry, you are not verified to upload packets.")
                else:
                    print("processing...")
                    await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name="processing quizbowl packets"))
                    current_action="processing"

                    #save the attached packet, prompt for one if none exists
                    if len(message.attachments) == 0:
                        await message.channel.send("No attachment detected - please try again but with a packet attached")
                        print("Resetting to idle mode")
                        await client.change_presence(status=discord.Status.idle)
                        current_action = "waiting"

                    else:
                        try:
                            print(message.attachments[0].url + " recieved")
                            #I figure out what kind of file it is by checking the url. I'm not super happy with this method because there's a lot of ways it could go wrong either intentionally or unintentionally, so if you can come up with a smarter way of doing this feel free.
                            if ".txt" in message.attachments[0].url.lower():
                                await message.channel.send("Oh my goodness thanks so much for sending a plain text file you don't know how much easier this makes things for me <3. Let's just hope it's formatted well, otherwise we might be in trouble.")
                                await message.attachments[0].save("processed_packet_data")
                                print("processed_packet_data saved")
                            elif ".pdf" in message.attachments[0].url.lower() or ".doc" in message.attachments[0].url.lower():
                                await message.attachments[0].save("raw_packet_data")
                                print("raw_packet_data saved")
                            else:
                                await message.channel.send("I was unable to figure out what kind of file that is you're sending. Please send either a .txt file, a .pdf file, or a .docx file.")
                                print("Resetting to idle mode")
                                await client.change_presence(status=discord.Status.idle)
                                current_action = "waiting"

                            #convert pdf packets to text (Honestly, I have no idea how this works. If you're editing this and you want help from me, you're on your own kid. I just copied this from stack overflow)
                            if ".pdf" in message.attachments[0].url.lower():
                                print("handling pdf packet")
                                await message.channel.send("The PDF packet file you sent is being converted to a text file. This will take a few minutes, please bear with me!")
                                with open("raw_packet_data", "rb")as raw_pdf, open("processed_packet_data", "w") as text_file:
                                    resource_manager = PDFResourceManager()
                                    converter = TextConverter(resource_manager, text_file, laparams=LAParams())
                                    page_interpreter = PDFPageInterpreter(resource_manager, converter)
                                    page_index = 1
                                    for page in PDFPage.get_pages(raw_pdf, caching=True, check_extractable=True):
                                        page_interpreter.process_page(page)
                                        print("Page " + str(page_index) + " processed.")
                                        await message.channel.send("Page " + str (page_index) + " has been converted to text")
                                        page_index += 1
                                converter.close()
                                await message.channel.send("PDF conversion complete")

                            #If you can get python-docx working on your machine, you can probably handle .docx packets in a much nicer way. I couldn't get it to work somehow.
                            if ".doc" in message.attachments[0].url.lower():
                                print("handling docx packet")
                                await message.channel.send("It looks like you've sent me a docx packet. Let's try to parse it!")
                                with open("processed_packet_data", "w") as text_file:
                                    print(docx2txt.process("raw_packet_data"), file=text_file)
                                    print(".docx conversion complete")
                                    await message.channel.send("Alright, I've converted your .docx file to a .txt file")

                            #Create a directory, and then divide up the packet into question subunits based on common formatting features (weirdly formatted packets will 100% break this step)
                            print("commencing slicy-dicey")
                            await message.channel.send("I'm creating a folder system to store your questions")
                            if len(args) == 1:
                                await message.channel.send("No name specified; saving packet over \"default\"")
                                packet_name = "default"
                            else:
                                await message.channel.send("Saving packet as " + args[1])
                                packet_name = args[1]
                            if os.path.exists("packets/" + packet_name):
                                print("overwriting...")
                            else:
                                os.mkdir("packets/" + packet_name)
                                os.mkdir("packets/" + packet_name + "/tossups")
                                os.mkdir("packets/" + packet_name + "/bonuses")
                                for i in range (1,21):
                                    os.mkdir("packets/" + packet_name + "/tossups/" + str(i))
                                    os.mkdir("packets/" + packet_name + "/bonuses/" + str(i))
                                print("directories created")
                            await message.channel.send("Here we go, let's try and break down this text file into all the relevant question components")
                            #divide the packet text by empty lines
                            f = open("processed_packet_data", "r")
                            text = f.read()
                            f.close()
                            paragraphs = re.split("\n\s+\n|\n\n", text)
                            print(paragraphs)
                            #Remove whitespace at the beginning of paragraphs and get rid of empty paragraphs resulting from several empty lines in a row in the original file
                            i = 0
                            while i < len(paragraphs):
                                paragraphs[i] = paragraphs[i].lstrip()
                                if paragraphs[i] == "":
                                    paragraphs.pop(i)
                                else:
                                    i += 1
                            #Adding in an empty line at the begginning bc that was the nicest way I could figure out to make the next bit work
                            paragraphs.insert(0, "")
                            #We determine what things are tossups by figuring out what comes right before "ANSWER:"
                            question_number = 1
                            while question_number <= 20:
                                #Search for ANSWER:, then look for the tossup in either the same paragraph or the one beofre
                                if "ANSWER:" in paragraphs[1]:
                                    if paragraphs[1].startswith("ANSWER:"):
                                        print("Seperate lines, nice!")
                                    else:
                                        paragraphs[0] = paragraphs[1].split("ANSWER:", 1)[0]
                                        paragraphs[1] = "ANSWER:" + paragraphs[1].split("ANSWER:", 1)[1]
                                        print("Splitting paragraph!")
                                    cur_path = ("packets/" + packet_name + "/tossups/" + str(question_number) + "/")
                                    f = open(cur_path + "answer", "w")
                                    f.write(paragraphs[1])
                                    f.close()
                                    clues = paragraphs[0].split(". ")
                                    #remove all empty clues
                                    clues = [j for j in clues if re.search('[a-zA-Z]', j)]
                                    for j in range(len(clues)):
                                        f = open(cur_path + "clue" + str(j), "w")
                                        f.write(clues[j])
                                        f.close()
                                    print("Tossup " + str(question_number) + " split n' saved!")
                                    question_number += 1
                                paragraphs.pop(0)

                            #Now we have to handle the bonuses. First, we have to get to the first bonus. Because otherwise we cannot tell bonuses and extra tossups apart, we're going to assume all bonus leadins include "for ten points each" or "ftpe".
                            while not (" points each" in paragraphs[0].lower() or "ftpe" in paragraphs[0].lower()):
                                paragraphs.pop(0)
                            #Now we've reached the bonuses. Each bonus has 7 parts, but they're not always subdivided right. So, we do it ourselves.
                            question_number = 1
                            while question_number <= 20:
                                if question_number != 20:
                                    while not ((("10" in paragraphs[1].lower() or "ten" in paragraphs[1].lower()) and "points" in paragraphs[1].lower() and "each" in paragraphs[1].lower()) or "ftpe" in paragraphs[1].lower()):
                                        paragraphs[0] = paragraphs[0] + paragraphs [1]
                                        paragraphs.pop(1)
                                else:
                                    paragraphs = ["".join(paragraphs)]
                                paragraphs[0] = paragraphs[0].replace("ANSWER:", "[10]")
                                bonus_subdivisions = paragraphs[0].split("[10]")
                                if len(bonus_subdivisions) < 7:
                                    print("bonus handling failed; not enough subdivisions. this packet's bonuses cannot be processed.")
                                    return
                                else:
                                    cur_path = ("packets/" + packet_name + "/bonuses/" + str(question_number) + "/")
                                    f = open(cur_path + "leadin", "w")
                                    f.write(bonus_subdivisions[0])
                                    f.close()
                                    f = open(cur_path + "part0", "w")
                                    f.write("[10]" + bonus_subdivisions[1])
                                    f.close()
                                    f = open(cur_path + "answer0", "w")
                                    f.write("ANSWER:" + bonus_subdivisions[2])
                                    f.close()
                                    f = open(cur_path + "part1", "w")
                                    f.write("[10]" + bonus_subdivisions[3])
                                    f.close()
                                    f = open(cur_path + "answer1", "w")
                                    f.write("ANSWER:" + bonus_subdivisions[4])
                                    f.close()
                                    f = open(cur_path + "part2", "w")
                                    f.write("[10]" + bonus_subdivisions[5])
                                    f.close()
                                    f = open(cur_path + "answer2", "w")
                                    f.write("ANSWER:" + bonus_subdivisions[6])
                                    f.close()
                                print("Bonus " + str(question_number) + "split n' saved!")
                                paragraphs.pop(0)
                                question_number += 1
                        except Exception as e:
                            await message.channel.send("An error occured while processing your file.")
                            print(e)
                        else:
                            await message.channel.send("Your file has been processed!")
                        await client.change_presence(status=discord.Status.idle)
                        current_action = "waiting"
                        print("waiting...")

            elif args[0] == "<help" or args[0] == "<?":
                await message.channel.send("Hello! I'm Quizbowl Practice Bot! Here's a list of things I can do! \n - \"<scorekeep\" tells me to keep a running total of two teams' scores \n - \"<process [name]\" with a packet attached in a docx, txt or pdf file will parse and save that file under the name [name]. (note: this function only available for people with the \"trusted uploader\" role) \n - \"<bonus [packet]\" tells me to read through the packet named [packet], assuming its been uploaded \n - \"<slowbowl_cooperative [packet]\" will tell me to read the packet named [packet] for a single team game of slowbowl \n - \"slowbowl_competitive [packet]\" will have me read two team slowbowl")

            else:
                await message.channel.send("I'm sorry, I don't understand the command \"" + args[0] + "\". If you want to see a list of all valid commands, try \"<help\"")

        #handle scorekeeping
        elif current_action == "scorekeeping":

            #add points to team 1
            if args[0] == "<team1":
                print("Adding " + args[1] + " to team 1's score")
                score1 += int(args[1])
                if score1 == score2:
                    await message.channel.send("The scores are tied at " + str(score1) + "!")
                elif score1 > score2:
                    await message.channel.send("Team 1 is winning " + str(score1) + " to " + str(score2) + "!")
                elif score1 < score2:
                    if int(args[1]) > 0:
                        await message.channel.send("Team 1 is losing " + str(score1) + " to " + str(score2) + ", but they're catching up!")
                    elif int(args[1]) < 0:
                        await message.channel.send("Team 1 is losing " + str(score1) + " to " + str(score2) + ". Maybe they should try not negging? idk just a suggestion what do I know I'm just your bot you don't have to listen to me")

            #add points to team 2
            if args[0] == "<team2":
                print("Adding " + args[1] + " to team 2's score")
                score2 += int(args[1])
                if score2 == score1:
                    await message.channel.send("The scores are tied at " + str(score1) + "!")
                elif score2 > score1:
                    await message.channel.send("Team 2 is winning " + str(score1) + " to " + str(score2) + "!")
                elif score2 < score1:
                    if int(args[1]) > 0:
                        await message.channel.send("Team 2 is losing " + str(score1) + " to " + str(score2) + ", but they're catching up!")
                    elif int(args[1]) < 0:
                        await message.channel.send("Team 2 is losing " + str(score1) + " to " + str(score2) + ". Maybe they should try not negging? idk just a suggestion what do I know I'm just your bot you don't have to listen to me")

            #end the scorekeeping
            if args[0] == "<end":
                print("Ending scorekeeping")
                if score1==score2:
                    await message.channel.send("Ooooh, ending on a tie, are we? Couldn't be bothered to do a tiebreaker? Alright, I guess we're *all* losers! I hope you're happy!")
                elif score1 > score2:
                    await message.channel.send("Congragulations, team 1 won " + str(score1) + " to " + str(score2) + "!")
                elif score1 < score2:
                    await message.channel.send("Congragulations, team 2 won " + str(score1) + " to " + str(score2) + "!")
                print("Resetting to idle mode")
                await client.change_presence(status=discord.Status.idle)
                current_action = "waiting"
                score1 = 0
                score2 = 0
                print("waiting...")




        #Handle bonus reading
        elif current_action == "reading bonuses":

            #read the next bonus
            if args[0] == "<guess":
                print("Guess recieved")
                print("reading bonus answer")
                f = open("packets/" + packet + "/bonuses/" + str(on_question[0]) + "/answer" + str(on_question[1]), "r")
                text = f.read()
                f.close()
                await message.channel.send(text)
                if on_question == [20,2]:
                    await message.channel.send("Ok, that's the end of the packet! Thanks for playing! (also btw I'm sorry if there was some extra nonsense at the end of the last answer. That happens sometimes)")
                    await client.change_presence(status=discord.Status.idle)
                    current_action="waiting"
                    print("waiting...")
                else:
                    if on_question[1] == 2:
                        on_question[0] += 1
                        on_question[1] -= 2
                    else:
                        on_question[1] += 1
                    print("reading next bonus part")
                    await message.channel.send("---------------")
                    if on_question[1] == 0:
                        f = open("packets/" + packet + "/bonuses/" + str(on_question[0]) + "/leadin", "r")
                        text = f.read()
                        f.close()
                        await message.channel.send(text)
                    f = open("packets/" + packet + "/bonuses/" + str(on_question[0]) + "/part" + str(on_question[1]), "r")
                    text = f.read()
                    f.close()
                    await message.channel.send(text)

            #end the reading prematurely
            if args[0] == "<end":
                print("ending bonus reading")
                await client.change_presence(status=discord.Status.idle)
                current_action="waiting"
                print("waiting...")
                await message.channel.send("Alright, that's a wrap!")


        #handle coop slowbowl
        elif current_action == "cooperative slowbowl":

            if args[0] == "<next":
                if os.path.exists("packets/" + packet + "/tossups/" + str(on_question[0]) + "/clue" + str(on_question[1]+1)):
                    on_question[1] += 1
                    f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/clue" + str(on_question[1]), "r")
                    text = f.read()
                    f.close()
                    await message.channel.send(text)
                else:
                    await message.channel.send("This is the end of the question. If you really have no idea, just guess Smith I suppose")

            elif args[0] == "<guess":
                f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/answer", "r")
                text = f.read()
                f.close
                await message.channel.send(text)
                await message.channel.send("Were you right? Send the message \"y\" for yes, or \"n\" for no.")
                def check(m):
                    return (m.content == "y" or m.content == "n") and m.channel == message.channel
                response = await client.wait_for("message", check=check)
                if response.content == "y":
                    max_points = len(os.listdir("packets/" + packet + "/tossups/" + str(on_question[0])))
                    score1 += (max_points - on_question[1])
                    await message.channel.send("Hey, nice! You scored " + str(max_points - on_question[1]) + " points on that question (out of a maximum possible score of " + str(max_points) + "), bringing your total score to " + str(score1) + "!")
                else:
                    await message.channel.send("Well, no risk no reward! You'll get the next one.")
                on_question[0] += 1
                on_question[1] = 0
                if on_question[0] == 21:
                    await message.channel.send("Aaaaaaand that's the game! You had a final score of " + str(score1) + " points out of a maximum possible score of " + str(score2) + " points! Idk what that means, but it sure sounds impressive! See ya next time, folks!")
                    score1 = 0
                    score2 = 0
                    print("ending coop slowbowl")
                    await client.change_presence(status=discord.Status.idle)
                    current_action="waiting"
                else:
                    await message.channel.send("---------------")
                    f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/clue" + str(on_question[1]), "r")
                    text = f.read()
                    f.close()
                    await message.channel.send(text)

            elif args[0] == "<end":
                print("ending slowbowl")
                await client.change_presence(status=discord.Status.idle)
                current_action="waiting"
                print("waiting...")
                score1 = 0
                score2 = 0
                await message.channel.send("Ok, fair enough, we'll call it here. Stay safe y'all!")


        elif current_action == "competitive slowbowl":
            if message.channel.name == "slowbowl-1":
                team = 1
            elif message.channel.name == "slowbowl-2":
                team = 2
            else:
                await message.channel.send("Sorry, I'm running competitive slowbowl right now and so cannot respond to messages outside of the slowbowl channels.")
                return

            if args[0] == "<next":
                if team == 1:
                    if slowbowl_teamstates[0] == "waiting":
                        await message.channel.send("Action confirmed")
                        slowbowl_teamstates[0] = "next"
                        if slowbowl_teamstates[1] == "waiting":
                            await discord.utils.get(message.channel.guild.text_channels, name="slowbowl-2").send("Team 1 has confirmed their action. The game is waiting on you!")
                        elif slowbowl_teamstates[1] == "checking":
                            print("no nudge sent; already answer checking")
                        else:
                            print("running resolution")
                            await resolve(message)
                    else:
                        await message.channel.send("You have already confirmed an action")

                elif team == 2:
                    if slowbowl_teamstates[1] == "waiting":
                        await message.channel.send("Action confirmed")
                        slowbowl_teamstates[1] = "next"
                        if slowbowl_teamstates[0] == "waiting":
                            await discord.utils.get(message.channel.guild.text_channels, name="slowbowl-1").send("Team 2 has confirmed their action. The game is waiting on you!")
                        elif slowbowl_teamstates[0] == "checking":
                            print("no nudge sent; already answer checking")
                        else:
                            print("running resolution")
                            await resolve(message)
                    else:
                        await message.channel.send("You have already confirmed an action")

            elif args[0] == "<guess":
                if team == 1:
                    if slowbowl_teamstates[0] == "waiting":
                        slowbowl_teamstates[0] = "checking"
                        f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/answer")
                        answer = f.read()
                        f.close()
                        await message.channel.send(answer)
                        team1_answer = message.content
                        await message.channel.send("Were you right? Send the message \"y\" for yes, or \"n\" for no. (Prompts are counted as no unless you specified the correct answer as a condition on being prompted in your answer).")
                        def check(m):
                            return (m.content == "y" or m.content == "n") and m.channel == message.channel
                        response = await client.wait_for("message", check=check)
                        if response.content == "y":
                            await message.channel.send("Excellent. Show no mercy.")
                            slowbowl_teamstates[0] = "correct"
                        if response.content == "n":
                            await message.channel.send("Unfortunate. Your opponents will be sure to take advantage of this error.")
                            slowbowl_teamstates[0] = "incorrect"
                        if slowbowl_teamstates[1] == "waiting":
                            await discord.utils.get(message.channel.guild.text_channels, name="slowbowl-2").send("Team 1 has confirmed their action. The game is waiting on you!")
                        elif slowbowl_teamstates[1] == "checking":
                            print("no nudge sent; already answer checking")
                        else:
                            print("running resolution")
                            await resolve(message)
                    else:
                        await message.channel.send("You have already confirmed an action")

                elif team == 2:
                    if slowbowl_teamstates[1] == "waiting":
                        slowbowl_teamstates[1] = "checking"
                        f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/answer")
                        answer = f.read()
                        f.close()
                        await message.channel.send(answer)
                        team2_answer = message.content
                        await message.channel.send("Were you right? Send the message \"y\" for yes, or \"n\" for no. (Prompts are counted as no unless you specified the correct answer as a condition on being prompted in your answer).")
                        def check(m):
                            return (m.content == "y" or m.content == "n") and m.channel == message.channel
                        response = await client.wait_for("message", check=check)
                        if response.content == "y":
                            await message.channel.send("Excellent. Show no mercy.")
                            slowbowl_teamstates[1] = "correct"
                        if response.content == "n":
                            await message.channel.send("Unfortunate. Your opponents will be sure to take advantage of this error.")
                            slowbowl_teamstates[1] = "incorrect"
                        if slowbowl_teamstates[0] == "waiting":
                            await discord.utils.get(message.channel.guild.text_channels, name="slowbowl-1").send("Team 1 has confirmed their action. The game is waiting on you!")
                        elif slowbowl_teamstates[0] == "checking":
                            print("no nudge sent; already answer checking")
                        else:
                            print("running resolution")
                            await resolve(message)
                    else:
                        await message.channel.send("You have already confirmed an action")

            elif args[0] == "<surrender":
                await message.channel.send("You make a tactical retreat. Lose the battle, win the war. They won't be ready for you next time...")
                if team == 1:
                    await discord.utils.get(message.channel.guild.text_channels, name="slowbowl-2").send("Team 1 has surrendered. You are victorious!")
                elif team == 2:
                    await discord.utils.get(message.channel.guild.text_channels, name="slowbowl-1").send("Team 2 has surrendered. You are victorious!")
                print("ending slowbowl")
                await client.change_presence(status=discord.Status.idle)
                current_action="waiting"
                print("waiting...")
                score1 = 0
                score2 = 0



#Handle proceeding a step in competitive slowbowl
async def resolve(message):
    global score1
    global score2
    global slowbowl_teamstates
    global packet
    global on_question
    global team1_answer
    global team2_answer
    channel1 = discord.utils.get(message.channel.guild.text_channels, name="slowbowl-1")
    channel2 = discord.utils.get(message.channel.guild.text_channels, name="slowbowl-2")
    f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/answer")
    answer = f.read()
    f.close()
    if slowbowl_teamstates == ["next", "next"]:
        print("proceeding to next clue")
        await channel1.send("Both teams have opted to recieve the next clue")
        await channel2.send("Both teams have opted to recieve the next clue")
        if os.path.exists("packets/" + packet + "/tossups/" + str(on_question[0]) + "/clue" + str(on_question[1]+1)):
            on_question[1] += 1
            f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/clue" + str(on_question[1]), "r")
            text = f.read()
            f.close()
            await channel1.send(text)
            await channel2.send(text)
        else:
            print("tried to proceed past end")
            await channel1.send("...however there is no next clue bc that was the end of the question. The answer was \"" + answer + "\". Moving on, I guess.")
            await channel2.send("...however there is no next clue bc that was the end of the question. The answer was \"" + answer + "\". Moving on, I guess.")
            await next(channel1, channel2)

    elif slowbowl_teamstates == ["correct", "next"]:
        print("team 1 takes it")
        await channel1.send("You got the question and the other team didn't, earning you 2 points! Press this advantage!")
        await channel2.send("Unfortunately, the other team got the question right and so earned 2 points. The answerline was \n \"" + answer + "\" \n, and they said \n \"" + team1_answer[6:] + "\" \n. If you think they shouldn't have got those points, argue it with them (I recommend single combat as a method of settling disputes if the disagreement still stands)")
        score1 += 2
        await channel1.send("You currently have a score of " + str(score1) + ", while your opponents have a score of " + str(score2))
        await channel2.send("You currently have a score of " + str(score2) + ", while your opponents have a score of " + str(score1))
        await next(channel1, channel2)

    elif slowbowl_teamstates == ["next", "correct"]:
        print("team 2 takes it")
        await channel2.send("You got the question and the other team didn't, earning you 2 points! Press this advantage!")
        await channel1.send("Unfortunately, the other team got the question right and so earned 2 points. The answer was \n\"" + answer + "\"\n, and they said \n\"" + team2_answer[6:] + "\"\n. If you think they shouldn't have got those points, argue it with them (I recommend single combat as a method of settling disputes if the disagreement still stands)")
        score2 += 2
        await channel1.send("You currently have a score of " + str(score1) + ", while your opponents have a score of " + str(score2))
        await channel2.send("You currently have a score of " + str(score2) + ", while your opponents have a score of " + str(score1))
        await next(channel1, channel2)

    elif slowbowl_teamstates == ["incorrect", "next"] or slowbowl_teamstates == ["incorrect", "correct"]:
        print("team1 negs")
        await channel1.send("The other team was not decieved, and so were awarded 2 points.")
        await channel2.send("The other team negged with \"" + team1_answer[6:] + "\". The answerline was \n" + answer + ". So, you are awarded 2 points.")
        score2 += 2
        await channel1.send("You currently have a score of " + str(score1) + ", while your opponents have a score of " + str(score2))
        await channel2.send("You currently have a score of " + str(score2) + ", while your opponents have a score of " + str(score1))
        await next(channel1, channel2)

    elif slowbowl_teamstates == ["next", "incorrect"] or slowbowl_teamstates == ["correct", "incorrect"]:
        print("team2 negs")
        await channel2.send("The other team was not decieved, and so were awarded 2 points.")
        await channel1.send("The other team negged with \"" + team2_answer[6:] + "\". The answerline was \n" + answer + ". So, you are awarded 2 points.")
        score1 += 2
        await channel1.send("You currently have a score of " + str(score1) + ", while your opponents have a score of " + str(score2))
        await channel2.send("You currently have a score of " + str(score2) + ", while your opponents have a score of " + str(score1))
        await next(channel1, channel2)

    elif slowbowl_teamstates == ["correct", "correct"]:
        await channel1.send("The other team was right too (they said \"" + team2_answer + "\"), but of course you were *more* right. Still, you both just get 1 point.")
        await channel2.send("The other team was right too (they said \"" + team1_answer + "\"), but of course you were *more* right. Still, you both just get 1 point.")
        score1 += 1
        score2 += 1
        await channel1.send("You currently have a score of " + str(score1) + ", while your opponents have a score of " + str(score2))
        await channel2.send("You currently have a score of " + str(score2) + ", while your opponents have a score of " + str(score1))
        await next(channel1, channel2)

    elif slowbowl_teamstates == ["incorrect", "incorrect"]:
        await channel1.send("The other team was wrong too lol (they said \"" + team2_answer + "\"). Nobody gets any points!")
        await channel2.send("The other team was wrong too lol (they said \"" + team1_answer + "\"). Nobody gets any points!")
        await channel1.send("You currently have a score of " + str(score1) + ", while your opponents have a score of " + str(score2))
        await channel2.send("You currently have a score of " + str(score2) + ", while your opponents have a score of " + str(score1))
        await next(channel1, channel2)
    slowbowl_teamstates = ["waiting", "waiting"]

#Show the next question in competitive slowbowl
async def next(ch1, ch2):
    print("getting next question")
    global on_question
    global packet
    global score1
    global score2
    global current_action
    on_question[1] = 0
    print("breakpoint 1")
    if on_question[0] == 2:
        await ch1.send("The game has finished! The final score was " + str(score1) + " to " + str(score2) + "!")
        await ch2.send("The game has finished! The final score was " + str(score1) + " to " + str(score2) + "!")
        if score1 == score2:
            await ch1.send("By the score it was a tie, but you know in your hearts that you were the victors")
            await ch2.send("By the score it was a tie, but you know in your hearts that you were the victors")
        elif score1 > score2:
            await ch1.send("You successfuly vanquished your foes! But at what cost?")
            await ch2.send("You have been defeated. But your enemies will not wear their laurels long, for your spite and anger will twist you into a brutal machine of destruction that will tear down their glory when next you face them!")
        elif score2 > score1:
            await ch2.send("You successfuly vanquished your foes! But at what cost?")
            await ch1.send("You have been defeated. But your enemies will not wear their laurels long, for your spite and anger will twist you into a brutal machine of destruction that will tear down their glory when next you face them!")
        await ch1.send("This concludes the match. Farewell!")
        await ch2.send("This concludes the match. Farewell!")
        print("ending slowbowl")
        await client.change_presence(status=discord.Status.idle)
        current_action="waiting"
        print("waiting...")
        score1 = 0
        score2 = 0
    else:
        print("breakpoint 2")
        on_question[0] += 1
        slowbowl_teamstates = ["waiting", "waiting"]
        print("breakpoint 3")
        f = open("packets/" + packet + "/tossups/" + str(on_question[0]) + "/clue0")
        text = f.read()
        f.close
        print("breakpoint 4")
        await ch1.send(text)
        await ch2.send(text)


client.run(token)




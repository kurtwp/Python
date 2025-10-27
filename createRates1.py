import random


with open("6-digit-dn.csv", "r",) as file:
    for lines in file:
        randomNumber = random.randint(1,10000)
        randomLength = len(str(randomNumber))
        # Below line is similar to the chomp fub=nction in Perl 
        line = lines.rstrip('\n')
        # -----------------------------------------------------
        if (randomLength == 4):
            with open("rates.txt", "a") as file:
                file.writelines(line + ",0." + str(randomNumber) + "\n")
        elif (randomLength == 3):
            with open("rates.txt", "a") as file:
                file.writelines(line + ",0.0" + str(randomNumber) + "\n")
        elif (randomLength == 2):
            with open("rates.txt", "a") as file:
                file.writelines(line + ",0.00" + str(randomNumber) + "\n")
        elif (randomLength == 3):
            with open("rates.txt", "a") as file:
                file.writelines(line + ",0.000" + str(randomNumber) + "\n")
        else:
            with open("rates.txt", "a") as file:
                file.writelines(line + ",0.0000" + str(randomNumber) + "\n")


import random
with open("6-digit-dn.csv", "r") as file:
    for lines in file:
        randomNumber = random.randint(1, 10000)
        line = lines.rstrip('\n') # Similar to chomp in perl
        formatted_rate = f"0.{randomNumber:04d}"  # ensures 4 digits with leading zeros - Similar to  my $formatted_number = sprintf("%04d", $random_number); in perl
        with open("rates.txt", "a") as outfile:
            outfile.writelines(f"{line},{formatted_rate}\n")

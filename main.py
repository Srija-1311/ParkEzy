import os
import separation
import evaluate

def main():

    if not os.path.exists("data/UFPR04/images"):
        print("Dataset not separated. Running separation...")
        separation.run()

    print("Running evaluation...")
    evaluate.run()

if __name__ == "__main__":
    main()

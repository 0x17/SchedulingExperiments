import sys
import model

def main(args):
    results = model.solve('j3010_1.json')
    print(results)

if __name__ == '__main__':
    main(sys.argv)
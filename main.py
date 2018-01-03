import sys
import model
import validation
import basedata


def main(args):
    results = model.solve('j3010_1.json')
    print(results)
    model.serialize_results(results)
    validation.validate_schedule_and_profit('j3010_1.sm')


if __name__ == '__main__':
    main(sys.argv)

import os
import sys

exts = ['o', 'ppu', 'DAT']

def force_delete_file(fn):
    while True:
        try:
            if not (os.path.isfile(fn)): break
            os.remove(fn)
        except OSError:
            print('Deleting ' + fn + ' failed. Retry!')
        else:
            break

def has_ext(fn):
	return any([ fn.endswith(ext) for ext in exts ])

def main(args = []):
	print('Cleaning up PROGEN')
	for fn in os.listdir('.'):
		if has_ext(fn):
			print('Removing {0}'.format(fn))
			force_delete_file(fn)
		
if __name__ == '__main__':
	main(sys.argv)

# Copyright (c) 2020 Jeffrey A. Webb

default:

clean:
	py3clean .
	find . -name '*~' | xargs rm -f
	rm -f out.svg

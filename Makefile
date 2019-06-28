all: build install pull

build:
	@docker build --tag=anthonyrawlinsuom/stevejobs .

install:
	@docker push anthonyrawlinsuom/stevejobs
	
pull:
	@docker pull anthonyrawlinsuom/stevejobs

minor:
	./minor.sh

patch:
	./patch.sh

major:
	./major.sh

clean:
	@docker rmi --force anthonyrawlinsuom/stevejobs

stevejobs:
	@docker build --tag=anthonyrawlinsuom/stevejobs .
	@docker push anthonyrawlinsuom/stevejobs

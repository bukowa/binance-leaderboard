PROXY_FILE=proxies.json

setup: req

req:
	pip install -r requirements.txt

1: req
	python ./getleaderboardrank.py
	python ./getpositionstatus.py

2: 1
	python ./getotherperformance.py

3: 1 2 parse_positions_proxies

4: 1 2 parse_positions

parse_positions:
	python ./getotherposition.py

parse_positions_proxies: proxies proxies/output parse_positions proxies/delete

proxies:
	terraform init
	terraform apply --auto-approve

proxies/delete:
	terraform destroy --auto-approve
	rm $(PROXY_FILE) || true

proxies/output:
	@terraform refresh > /dev/null
	@terraform output --json | jq '.ips.value' > $(PROXY_FILE)
	@cat $(PROXY_FILE)

.PHONY:setup req all proxies proxies/delete proxies/output parse_positions parse_positions_proxies 1 2 3

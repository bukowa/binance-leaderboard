
.PHONY: proxies
proxies:
	terraform apply --auto-approve

.PHONY: proxies/delete
proxies/delete:
	terraform destroy --auto-approve

.PHONY: output
output:
	@terraform refresh > /dev/null
	@terraform output --json | jq '.ips.value' > proxies.json
	@cat proxies.json


.PHONY: parse_traders
parse_traders:
	python parse_traders.py

.PHONY: parse_positions
parse_positions:
	python parse_positions.py

.PHONY: parse_position_proxy
parse_positions_proxy: proxies output parse_positions

.PHONY: parse_table
parse_table:
	@python parse_table.py > index.html
	@brave-browser index.html || true

all: parse_traders parse_positions_proxy parse_table

.PHONY: notebook
notebook:
	jupyter notebook

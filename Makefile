
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

.PHONY: browse
browse:
	@brave-browser index.html || true

all: parse_traders parse_positions_proxy parse_table

.PHONY: notebook
notebook:
	jupyter notebook

FFILE=./function/packages/table/tablesorter/tablesorter.py
FNAME=table/tablesorter
FNAMESPACE=binance-leaderboard-test

.PHONY: function
function: parse_table
	printf 'data="""\n\n' > $(FFILE)
	cat index.html >> $(FFILE)
	printf '\n\n"""\n\n' >> $(FFILE)
	echo "def main(args):" >> $(FFILE) && \
    echo "	return dict(body=data)"  >> $(FFILE) && \
    doctl serverless install
	doctl serverless connect $(FNAMESPACE)
	doctl serverless deploy ./function
	doctl serverless functions get -r $(FNAME)

.PHONY: fresh
fresh: parse_positions_proxy proxies/delete function
.PHONY: main
main:
	$(MAKE) -C ./binance 4
	$(MAKE) parse_table
	$(MAKE) browse || true

.PHONY: parse_table
parse_table:
	@python parse_table.py > index.html

.PHONY: browse
browse:
	@brave-browser index.html || true

.PHONY: notebook
notebook:
	jupyter-lab


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

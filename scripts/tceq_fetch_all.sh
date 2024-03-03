set -e

for i in {0..110}; do
    echo "Fetching page $((i))"
    wget  "https://records.tceq.texas.gov/cs/idcplg?IdcService=TCEQ_PERFORM_SEARCH&QueryText=%28%3cftx%3eMAERT%3c%2fftx%3e%29++%3cAND%3e++%28dSecurityGroup+%3cmatches%3e+%60Public%60%3cAND%3exRecordSeries%3cmatches%3e%601081%60%29&SortField=&SortOrder=Desc&ResultCount=100000&SearchEngineName=ELASTICSEARCH&SearchQueryFormat=UNIVERSAL&searchFormType=standard&listTemplateId=SearchResultsHeadline&SearchProviders=tceq4avrwccecmp_4444&SortSpec=xRecordSeries%20asc%2cxPrimaryID%20asc%2cxSecondaryID%20asc%2cxInsightDocumentType%20asc%2cdDocTitle%20asc%2cxBeginDate%20asc&SearchEngineName=ELASTICSEARCH&&IsExternalSearch=1&PageNumber=$((i+1))&StartRow=$((100000*i+1))&EndRow=$((100000*(i+1)))&columnsString=dDocName,xRecordSeries,xPrimaryID,xSecondaryID,xInsightDocumentType,dDocTitle,xBeginDate,xEndDate,xLitigationHold,xRegEntName,xMedia,xComments,dSecurityGroup&accessID=4236079&newSearch=0" -O "$HOME/data/texas_air/tceq/tceq_allhk_$((i)).html"
    sleep 1
done

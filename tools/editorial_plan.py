#!/usr/bin/env python3
"""Generate a LOCAL, review-only editorial plan. Never auto-publish or infer demand.

No network/API call, credentials, fabricated trend score or product substitution.
Reads the same source-linked publication register as the site. Optional summary
comes from the local first-party collector export; no individual data is accepted.
"""
from __future__ import annotations
import argparse
from datetime import date,timedelta
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def plan(today=None):
    today=today or date.today()
    monday=today+timedelta(days=(7-today.weekday())%7)
    guides=json.loads((ROOT/'content/guides.json').read_text())
    publication=json.loads((ROOT/'content/publication.json').read_text())
    return {
        'generated_on':today.isoformat(),
        'state':'REVIEW_ONLY_NO_PUBLICATION',
        'proposed_next_review':monday.isoformat(),
        'cadence':'Proposed Monday review; not an automatic publishing commitment.',
        'measured_demand':None,
        'authorized_report_state':'No report supplied; never label the following hypotheses as trending or high-converting.',
        'review_candidates':[{'guide':g['title'],'path':'guides/'+g['slug']+'.html','action':'Refresh exact-model sources and open conflicts before considering a new draft.','state':'EDITORIAL_HYPOTHESIS','official_context':[publication['sources'][sid]['url'] for sid in sorted({x for section in g['sections'] for x in section['sources']})]} for g in guides],
        'seasonal_cluster':{'label':'Planning shared meals','state':'DRAFT_EDITORIAL_HYPOTHESIS','demand_evidence':None,'angle':'Capacity/layout planning and safe temperature checks for the food you actually cook; no holiday-deal, trend, portion or test claim.','guide_paths':['guides/air-fryer-capacity.html','guides/instant-read-or-wireless.html']},
        'before_publish':['Verify intended products separately from observed destinations.','Validate one enrolled-workflow link/report per product before scaling.','Read exact official model sources; leave unknowns blank.','Review sources, disclosure, image rights, authorship and mobile/keyboard behavior.','Review proposed changes on suggestions.html; no local preference auto-approves a change.','Build guides, canonical sitemap and RSS together; run all CI and packaged-site gates.'],
        'external_gates':['Permanent measurement hosting','Enrolled Associates workflow/report','Search Console ownership and authorized query report','Responsible human editorial/privacy contact','Authorized AI/API service, if future automation is chosen']
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=ROOT/'.local/editorial-plan.json')
    args=ap.parse_args()
    target=args.out.resolve()
    # Plans belong outside the published paths. Refuse to overwrite source/output pages.
    if not target.is_relative_to(ROOT/'.local') or target.suffix!='.json':
        ap.error('Write draft plans only under the ignored .local/ directory as JSON')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(plan(),ensure_ascii=False,indent=2)+'\n')
    print('Review-only plan written; no published content, link, metric or decision changed.')


if __name__=='__main__':main()

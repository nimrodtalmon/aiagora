"""Figure for paper/scale: (a) windows of community sizes per activity, broadcast vs agora;
(b) number of activities that happen vs community size. Reads runs/scale*.csv."""
import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
win = list(csv.DictReader(open(os.path.join(ROOT, 'runs', 'scale_windows.csv'))))[:24]
cnt = list(csv.DictReader(open(os.path.join(ROOT, 'runs', 'scale.csv'))))
OR, DK, LT = '#E8731D', '#26282C', '#F2B27E'
plt.rcParams.update({'font.size': 9, 'font.family': 'sans-serif'})
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
for r in win:
    t = int(r['t'])
    ax[0].plot([int(r['agora0_from']), 1000], [t + 0.17, t + 0.17], color=OR, lw=2.2, solid_capstyle='butt')
    if r['b_lo']:
        ax[0].plot([int(r['b_lo']), int(r['b_hi'])], [t - 0.17, t - 0.17], color=DK, lw=2.2, solid_capstyle='butt')
ax[0].set_xscale('log'); ax[0].set_xlim(4, 1000); ax[0].set_ylim(24.8, 0.2)
ax[0].set_xlabel('community size n'); ax[0].set_ylabel('activity t (share 0.5/t)')
ax[0].plot([], [], color=DK, lw=2.2, label='broadcast'); ax[0].plot([], [], color=OR, lw=2.2, label='agora, err = 0')
ax[0].legend(frameon=False, loc='lower left', fontsize=8)
ax[0].set_title('(a) sizes at which an activity happens', fontsize=9)
ns = [int(r['n']) for r in cnt]
ax[1].plot(ns, [int(r['agora_err0']) for r in cnt], color=OR, lw=1.8, label='agora, err = 0')
ax[1].plot(ns, [int(r['agora_err10']) for r in cnt], color=LT, lw=1.8, label='agora, err = 10')
ax[1].plot(ns, [int(r['broadcast']) for r in cnt], color=DK, lw=1.8, label='broadcast')
ax[1].set_xscale('log'); ax[1].set_xlim(4, 20000)
ax[1].set_xlabel('community size n'); ax[1].set_ylabel('activities that happen')
ax[1].legend(frameon=False, loc='upper left', fontsize=8)
ax[1].set_title('(b) number of activities that happen', fontsize=9)
for a in ax:
    a.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(ROOT, 'paper', 'scale', 'scale.pdf'))
print('wrote paper/scale/scale.pdf')

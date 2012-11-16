import matplotlib
matplotlib.use("Agg") # do this before pylab so you don'tget the default back end.
from matplotlib.pyplot import *
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset
import matplotlib.transforms as mtransforms
from mpl_toolkits.axes_grid1 import Grid
import subprocess
import re

# gather data
platform = "cortex-a8"
benchmark = "fdct"

measurements = [[1,1,1],[1,1,1],[1,1,1]]
measurements_Os = [1,1,1]

def getmm(p,b, directory, test):
    try:
        p = subprocess.Popen("getresult -c {}/{}/{}/{}/results".format(directory,p,b,test), shell=True, stdout=subprocess.PIPE)
        p.wait()
        if p.returncode != 0:
            return [1.0, 1.0, 1.0]
        m = re.split(r"\s*,\s*", p.communicate()[0])
        m = map(float, m)
        return m
    except IOError:
        return [1.0, 1.0, 1.0]

ymin = 1.
ymax = 1.

m1 = getmm(platform, benchmark, "testing_all", "3fc000000000000000000000000000000000")
m2 = getmm(platform, benchmark, "testing_all", "3ffffffffffe000000000000000000000000")
m3 = getmm(platform, benchmark, "testing_all", "3fffffffffffffffffffe000000000000000")
m4 = getmm(platform, benchmark, "testing_all", "3ffffffffffffffffffffff0000000000000")
m5 = getmm(platform, benchmark, "testing_all", "3ffffffffffffffffffffff0000800000000")
ms = getmm(platform, benchmark, "testing_all", "3cffffff7ffe1ffff7fde000000000000000")

ma1 = map(lambda x,y: x / y, m2, m1)
ma2 = map(lambda x,y: x / y, m3, m1)
ma3 = map(lambda x,y: x / y, m4, m1)
ma4 = map(lambda x,y: x / y, m5, m1)
mas = map(lambda x,y: x / y, ms, m1)

measurements = [ma1, ma2, ma3, ma4]
measurements_Os = mas

fig = figure(figsize=(10/3,8.5/5), dpi=1200)
ax = fig.add_subplot(111)

ymin = 0.
ymax = 1.5

ll = zip(*measurements)

n = sum(map(lambda x: x > 0.01, ll[0]))
x_r = range(n+1)
ll = map(lambda x: x[0:n], ll)

pl3 = ax.plot(x_r, [1.0] + list(ll[2]), '+-r', linewidth=0.5, label="Average power", markersize=10,markeredgewidth=1.3)
pl2 = ax.plot(x_r, [1.0] + list(ll[1]), 'x-c', linewidth=0.5, label="Execution time", markersize=10,markeredgewidth=1.3)
pl1 = ax.plot(x_r, [1.0] + list(ll[0]), '.-g', linewidth=0.5, label="Energy consumed", markersize=8, markeredgewidth=1.3)

if measurements_Os[0] > 0.01:
    ax.plot([4.7], measurements_Os[2], '+r', markersize=10,markeredgewidth=1.3)
    ax.plot([4.7], measurements_Os[1], 'xc', markersize=10,markeredgewidth=1.3)
    ax.plot([4.7], measurements_Os[0], '.g', markersize=8,markeredgewidth=1.3)

ax.set_ylim([0., 1.5])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5])
# ax.set_ylabel(benchmark, rotation="horizontal",zorder=-200)
ax.yaxis.tick_left()

ax.set_xticks([0, 1, 2, 3, 4, 4.7])
ax.set_xticklabels(["O0", "O1", "O2", "O3", "O4","Os"])
# ax.text(0.5,-0.33,platform,transform=ax.transAxes,ha='center',va='center')
ax.xaxis.tick_bottom()

ax.set_ylim([ymin, ymax])
ax.set_xlim([-0.4, 5.4])

ax.axhline(y=1, color="0.33", linestyle=":", linewidth=0.5)
ax.axhline(y=0.5, color="0.33", linestyle=":", linewidth=0.5)

bbox_ = mtransforms.Bbox.from_bounds(0, 0-0.5, 1., 1 + 0.5) # increase the height
bbox = mtransforms.TransformedBbox(bbox_, ax.transAxes)
pl1[0].set_clip_box(bbox)
pl2[0].set_clip_box(bbox)
pl3[0].set_clip_box(bbox)


# [label.set_visible(False) for label in ax.get_xticklabels()]

# axins = zoomed_inset_axes(parent_axes=ax_for_zoom_x, zoom=2, loc=10,
#                           bbox_to_anchor=(0.5, 0.),
#                           bbox_transform=ax_for_zoom_x.transAxes,
#                           axes_kwargs=dict(sharex=ax_for_zoom_x, sharey=ax_for_zoom_x),
#                           # borderpad=-2.5, #padding in fraction of font size
#                           )
# ax_for_zoom_x.transData.transform((5,0))
# pp, p1, p2 = mark_inset(parent_axes=ax_for_zoom_x, inset_axes=axins, loc1=3, loc2=4,
#                         fc=None, ec="0.5")
# pp.set_visible(False)

# axins.axesPatch.set_alpha(0.)



# # we want to draw the bottom spine only
# axins.set_frame_on(True)
# axins.spines['top'].set_visible(False)
# axins.spines['left'].set_visible(False)
# axins.spines['right'].set_visible(False)

# # don't draw the y axis ticks or labels
# axins.set_yticks([])
# axins.set_yticklabels([])

# # only draw the bottom (x) axes
# axins.xaxis.set_ticks_position('bottom')
# axins.xaxis.set_label_position('bottom')
# axins.set_xlim([-0.5, 5.5])
# axins.set_xticks([0, 1, 2, 3, 4, 4.7])
# axins.set_xticklabels(["O0", "O1", "O2", "O3", "O4","Os"])

# axins.set_xlabel('Optimization Level')

# [label.set_visible(False) for label in ax_for_zoom_x.get_xticklabels()]

# #################### y axis

# axins = zoomed_inset_axes(parent_axes=ax_for_zoom_y, zoom=3, loc=6,
#                           bbox_to_anchor=(0, 0.5),
#                           bbox_transform=ax_for_zoom_y.transAxes,
#                           axes_kwargs=dict(sharex=ax_for_zoom_y, sharey=ax_for_zoom_y),
#                           borderpad=-5, #padding in fraction of font size
#                           )

# pp, p1, p2 = mark_inset(parent_axes=ax_for_zoom_y, inset_axes=axins, loc1=2, loc2=3,
#                         ec="0.5", zorder=-10)
# pp.set_visible(False)
# pp.set_zorder(-10)
# p1.set_zorder(-10)
# p2.set_zorder(-10)

# axins.axesPatch.set_alpha(0.)

# l = matplotlib.lines.Line2D([-0.3,1.0],[1.0,1.0-1./6], color="0.5",linestyle=":")
# axins.add_line(l)
# l = matplotlib.lines.Line2D([-0.3,1.0],[0.5,1.0-2./6], color="0.5", linestyle=":")
# axins.add_line(l)

# # we want to draw the bottom spine only
# axins.set_frame_on(True)
# axins.spines['top'].set_visible(False)
# axins.spines['bottom'].set_visible(False)
# axins.spines['right'].set_visible(False)
# ##axins.set_zorder(-10)

# # don't draw the y axis ticks or labels
# axins.set_xticks([])
# axins.set_xticklabels([])

# # only draw the bottom (x) axes
# axins.yaxis.set_ticks_position('left')
# axins.yaxis.set_label_position('left')
# axins.set_ylim([0., 1.5])
# axins.set_yticks([0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5])

# axins.set_ylabel('Performance relative to O0')
# [label.set_visible(False) for label in ax_for_zoom_y.get_yticklabels()]

# ax1.legend(loc=3)
# fig.suptitle("Overall Optimization Levels for All Platform and Benchmark Combinations")

# handles, labels = ax.get_legend_handles_labels()
# fig.legend(handles, labels, 'lower left')
# print labels, handles

print ymin, ymax
fig.subplots_adjust(bottom=0.17, left=0.19, right=0.98)
# fig.savefig("/home/james/Dropbox/auto/levels.png", dpi=300)
# fig.savefig("/home/james/Dropbox/auto/levels.pdf")
fig.savefig("levels_one.png", dpi=300)
# fig.savefig("/home/james/Dropbox/auto/levels.pdf")
show()

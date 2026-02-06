# A custom widget for displaying a line chart of transaction data, used in the reports screen.
# It supports smooth animations when the data changes, and automatically scales the y-axis with nice round numbers.

import math
from math import ceil
from kivy.metrics import dp, sp
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse, Rectangle, RoundedRectangle
from kivy.core.text import Label as CoreLabel
from kivymd.app import MDApp
from kivy.properties import ListProperty, NumericProperty


class LineChart(Widget):
    values = ListProperty([])
    progress = NumericProperty(0)
    x_labels = ListProperty([])
    line_color = ListProperty([1, 0.2, 0.25, 1])
    dot_color = ListProperty([1, 0.25, 0.3, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.04, 0.05, 0.07, 0.5)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(14)]
            )

        with self.canvas:
            self._line_color_instr = Color(*self.line_color)
            self.line = Line(width=dp(3), cap="round", joint="round")

        self.bind(
            size=self.on_progress,
            pos=self.on_progress,
            values=self.on_progress,
            x_labels=self.on_progress,
        )
        self.bind(progress=self.on_progress, pos=self._update_bg, size=self._update_bg)
        self.bind(line_color=self._update_line_color)

    def _update_bg(self, *a):
        if hasattr(self, "_bg_rect"):
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size
            if hasattr(self._bg_rect, "radius"):
                self._bg_rect.radius = [dp(14)]

    def _update_line_color(self, *a):
        if hasattr(self, "_line_color_instr"):
            self._line_color_instr.rgba = self.line_color

    def _compute_points(self):
        w = max(1, self.width)
        h = max(1, self.height)

        gutter_left = dp(34)
        gutter_bottom = dp(24)
        padding_x = dp(16)
        padding_y = dp(12)

        plot_left = gutter_left + padding_x
        plot_bottom = gutter_bottom + padding_y

        usable_w = max(1, w - plot_left - padding_x)
        usable_h = max(1, h - plot_bottom - padding_y)

        chart_h = usable_h * 0.95
        if chart_h <= 0:
            chart_h = usable_h

        if not self.values:
            return [], plot_left, plot_bottom, usable_w, chart_h

        max_value = max(self.values) if self.values else 0

        points = []
        count = len(self.values)

        if count == 1:
            val = self.values[0]
            x = self.x + plot_left + usable_w / 2
            y = self.y + plot_bottom + self._scaled_y(val, max_value, chart_h)
            return [(x, y)], plot_left, plot_bottom, usable_w, chart_h

        for i, val in enumerate(self.values):
            x = self.x + plot_left + (usable_w / (count - 1)) * i
            y = self.y + plot_bottom + self._scaled_y(val, max_value, chart_h)
            points.append((x, y))

        return points, plot_left, plot_bottom, usable_w, chart_h

    def _scaled_y(self, val, max_value, chart_h):
        if max_value <= 0:
            return 0
        nice_max = self._nice_max(max_value)
        return (val / nice_max) * chart_h

    def _nice_max(self, value):
        if value <= 0:
            return 1
        exp = math.floor(math.log10(value))
        base = 10**exp
        scaled = value / base
        for step in (1, 1.5, 2, 2.5, 3, 5, 10):
            if scaled <= step:
                return step * base
        return 10 * base

    def _format_value(self, val):
        if val == 0:
            return "0"
        if val >= 1000:
            return f"{val:.0f}"
        if val >= 100:
            return f"{val:.0f}"
        if val >= 10:
            return f"{val:.1f}"
        return f"{val:.2f}"

    def set_data(self, values, x_labels=None):
        self.values = values
        if x_labels is not None:
            self.x_labels = x_labels
        self.progress = 0

        Animation.cancel_all(self)
        Animation(progress=1, d=0.9, t="out_cubic").start(self)

    def on_progress(self, *args):
        points, plot_left, plot_bottom, plot_w, plot_h = self._compute_points()
        if not points:
            self.line.points = []
            self.canvas.remove_group("dots")
            self._draw_axes(plot_left, plot_bottom, plot_w, plot_h)
            return

        self._draw_axes(plot_left, plot_bottom, plot_w, plot_h)

        n = len(points)

        if n == 1:
            if self.progress <= 0:
                self.line.points = []
                self._draw_dots(points, 0)
                return

            self.line.points = [points[0][0], points[0][1]]
            self._draw_dots(points, 1)
            return

        total_segment = n - 1
        seg_pos = self.progress * total_segment
        seg_idx = int(seg_pos)
        frac = seg_pos - seg_idx

        if seg_idx >= total_segment:
            seg_idx = total_segment - 1
            frac = 1.0

        smooth_points = self._smooth_points(points)
        if len(smooth_points) < 2:
            smooth_points = points

        total_seg = len(smooth_points) - 1
        seg_pos = self.progress * total_seg
        seg_idx = int(seg_pos)
        frac = seg_pos - seg_idx

        if seg_idx >= total_seg:
            seg_idx = total_seg - 1
            frac = 1.0

        draw_points = smooth_points[: seg_idx + 1]
        x1, y1 = smooth_points[seg_idx]
        x2, y2 = smooth_points[seg_idx + 1]
        xi = x1 + (x2 - x1) * frac
        yi = y1 + (y2 - y1) * frac
        draw_points.append((xi, yi))

        flat = []
        for x, y in draw_points:
            flat += [x, y]

        self.line.points = flat
        visible_count = (
            0 if self.progress <= 0 else min(n, int(self.progress * (n - 1)) + 1)
        )
        self._draw_dots(points, visible_count)

    def _draw_dots(self, points, visible_count):
        self.canvas.remove_group("dots")

        if visible_count <= 0:
            return

        with self.canvas:
            Color(*self.dot_color)
            size = dp(6)
            safe_count = min(visible_count, len(points))
            for i in range(safe_count):
                x, y = points[i]
                Ellipse(
                    pos=(x - size / 2, y - size / 2),
                    size=(size, size),
                    group="dots",
                )

    def _draw_axes(self, plot_left, plot_bottom, plot_w, plot_h):
        self.canvas.remove_group("axes")
        max_value = max(self.values) if self.values else 0
        nice_max = self._nice_max(max_value)

        y_ticks = 4
        x_labels = self.x_labels or []
        ox = self.x
        oy = self.y
        with self.canvas:
            Color(1, 1, 1, 0.12)
            Line(
                points=[
                    ox + plot_left,
                    oy + plot_bottom,
                    ox + plot_left,
                    oy + plot_bottom + plot_h,
                ],
                width=dp(1),
                group="axes",
            )
            for i in range(y_ticks + 1):
                t = i / y_ticks
                y = oy + plot_bottom + plot_h * t
                Line(
                    points=[ox + plot_left, y, ox + plot_left + plot_w, y],
                    width=dp(1),
                    group="axes",
                )

                val = nice_max * t
                self._draw_text(
                    self._format_value(val),
                    ox + plot_left - dp(6),
                    y,
                    halign="right",
                    valign="middle",
                    group="axes",
                )

            if x_labels:
                max_labels = 7
                step = max(1, ceil((len(x_labels) - 1) / max_labels))
                for i, label in enumerate(x_labels):
                    if i % step != 0 and i != len(x_labels) - 1:
                        continue
                    label_dx = 0
                    if i == len(x_labels) - 2:
                        label_dx = -dp(8)
                    if i == len(x_labels) - 1:
                        label_dx = -dp(4)
                    x = ox + plot_left + (plot_w / max(1, len(x_labels) - 1)) * i
                    self._draw_text(
                        label,
                        x + label_dx,
                        oy + plot_bottom - dp(6),
                        halign="center",
                        valign="top",
                        group="axes",
                    )

    def _draw_text(self, text, x, y, halign="center", valign="middle", group="axes"):
        label = CoreLabel(
            text=text,
            font_size=dp(14),
            color=(1, 1, 1, 1),
            font_name="Nunito-ExtraBold",
        )
        label.refresh()
        texture = label.texture
        if not texture:
            return
        tx = x
        ty = y
        if halign == "center":
            tx = x - texture.size[0] / 2
        elif halign == "right":
            tx = x - texture.size[0]
        if valign == "middle":
            ty = y - texture.size[1] / 2
        elif valign == "top":
            ty = y - texture.size[1]
        Rectangle(pos=(tx, ty), size=texture.size, texture=texture, group=group)
        Rectangle(pos=(tx, ty), size=texture.size, texture=texture, group=group)
        Rectangle(pos=(tx, ty), size=texture.size, texture=texture, group=group)
        Rectangle(pos=(tx, ty), size=texture.size, texture=texture, group=group)
        Rectangle(pos=(tx, ty), size=texture.size, texture=texture, group=group)

    def set_colors(self, line_rgba, dot_rgba=None):
        self.line_color = list(line_rgba)
        if dot_rgba is not None:
            self.dot_color = list(dot_rgba)

    def _smooth_points(self, points, samples=6):
        if len(points) < 3:
            return points

        out = [points[0]]
        for i in range(len(points) - 1):
            p0 = points[i - 1] if i - 1 >= 0 else points[i]
            p1 = points[i]
            p2 = points[i + 1]
            p3 = points[i + 2] if i + 2 < len(points) else points[i + 1]

            for s in range(1, samples + 1):
                t = s / (samples + 1)
                t2 = t * t
                t3 = t2 * t
                x = 0.5 * (
                    (2 * p1[0])
                    + (-p0[0] + p2[0]) * t
                    + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                    + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
                )
                y = 0.5 * (
                    (2 * p1[1])
                    + (-p0[1] + p2[1]) * t
                    + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                    + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
                )
                out.append((x, y))
            out.append(p2)

        return out

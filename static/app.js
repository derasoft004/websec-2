$(function () {
    let currentWeek = null;
    let prevWeek = null;
    let nextWeek = null;
    $('#btn-prev').on('click', function () {
        if (prevWeek) { currentWeek = prevWeek; loadSchedule(); }
    });

    $('#btn-next').on('click', function () {
        if (nextWeek) { currentWeek = nextWeek; loadSchedule(); }
    });

    function loadSchedule() {
        const params = {};
        if (currentWeek) params.week = currentWeek;

        $('#info-block, #week-block, #schedule-wrap, #empty-msg').hide();

        $.getJSON('/api/schedule', params)
            .done(function (data) {
                if (data.error) { alert('Ошибка: ' + data.error); return; }
                render(data);
            })
            .fail(function () {
                alert('Не удалось загрузить расписание');
            });
    }

    function buildLesson(l) {
        const m = l.type_class && l.type_class.match(/lesson-type-(\d+)/);
        const n = m ? m[1] : '4';
        const $l = $('<div>').addClass('lesson lt-' + n);

        $l.append($('<div class="lesson-badge">').text(l.type || ''));
        $l.append($('<div class="lesson-name">').text(l.discipline || ''));

        if (l.place) {
            $l.append($('<div class="lesson-meta">').html('<i class="mdi mdi-map-marker"></i> ' + l.place));
        }

        if (l.teacher) {
            const $t = $('<div class="lesson-meta">').append($('<i class="mdi mdi-account">'));
            if (l.teacher_href) {
                $('<a href="javascript:void(0)">').text(' ' + l.teacher).on('click', function () {
                    const tm = l.teacher_href.match(/staffId=(\d+)/);
                    if (tm) $.getJSON('/api/schedule', { staffId: tm[1] }).done(function (d) { if (!d.error) render(d); });
                }).appendTo($t);
            } else {
                $t.append(' ' + l.teacher);
            }
            $l.append($t);
        }

        if (l.subgroup) {
            $l.append($('<div class="lesson-meta text-muted">').text(l.subgroup));
        }

        if (l.groups && l.groups.length) {
            const $g = $('<div class="lesson-meta">');
            l.groups.forEach(function (g) {
                $('<a href="javascript:void(0)" class="badge badge-light mr-1">').text(g.name).on('click', function () {
                    const gm = g.href.match(/groupId=(\d+)/);
                    if (gm) { currentWeek = null; loadSchedule(); }
                }).appendTo($g);
            });
            $l.append($g);
        }

        return $l;
    }

    function render(data) {
        if (data.title) {
            $('#info-title').text(data.title);
            $('#info-desc').text(data.description || '');
            $('#info-block').show();
        }

        prevWeek = data.week_prev;
        nextWeek = data.week_next;
        $('#week-num').text(data.week);
        $('#week-date').text(data.week_date);
        $('#lbl-prev').text(prevWeek ? prevWeek + ' неделя' : '');
        $('#lbl-next').text(nextWeek ? nextWeek + ' неделя' : '');
        $('#btn-prev').prop('disabled', !prevWeek);
        $('#btn-next').prop('disabled', !nextWeek);

        const $wdNav = $('#weekday-nav').empty();

        data.days.forEach(function (d) {
            $('<div>')
                .append($('<div class="wd-name">').text(d.weekday))
                .append($('<div class="wd-date">').text(d.date.replace(/\.\d{4}/, '')))
                .appendTo($wdNav);
        });

        $('#week-block').show();

        const $hr = $('<tr>').append($('<th>').text('Время'));
        data.days.forEach(function (d) {
            $hr.append($('<th>').append($('<div class="dn">').text(d.weekday), $('<div class="dd">').text(d.date)));
        });
        $('#schedule-head').empty().append($hr);

        let hasLessons = false;
        const $body = $('#schedule-body').empty();

        data.rows.forEach(function (row) {
            const $tr = $('<tr>').append($('<td class="time-cell">').html(row.time.replace(' – ', '<br>')));
            row.days.forEach(function (lessons, di) {
                const $td = $('<td>').attr('data-day', di);
                lessons.forEach(function (l) {
                    hasLessons = true;
                    $td.append(buildLesson(l));
                });
                $tr.append($td);
            });
            $body.append($tr);
        });

        $('#schedule-wrap').toggle(hasLessons);
        $('#empty-msg').toggle(!hasLessons);
    }

    loadSchedule();
});

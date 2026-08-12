[
    {
        "role": "user",
        "content": "你理解错了，on_duty_time_result是0的时候是数据正常，你不要管别的字段，你就去on_duty里比较，上班时间九点，空的算迟到"
    },
    {
        "role": "assistant",
        "content": "SELECT u.username, COUNT(*) AS late_days FROM commute.assoc_bk_user_attendance_dd_eagle0922 a JOIN commute.assoc_bk_user u ON a.userid = u.id WHERE a.work_date BETWEEN '2025-08-01' AND '2025-08-31' AND a.is_work_day = 1 AND (a.on_duty IS NULL OR a.on_duty > '09:00:00') GROUP BY u.id, u.username ORDER BY late_days DESC"
    }
]
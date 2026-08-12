[
    {
        "role": "user",
        "content": "获取所有大学的排名和各方面评分，并按排名排序"
    },
    {
        "role": "assistant",
        "content": "SELECT u.University_Name, o.`Rank`, o.Reputation_point, o.Research_point, o.Citation_point, o.Total FROM university_rank.overall_ranking o JOIN university_rank.university u ON o.University_ID = u.University_ID ORDER BY o.`Rank` ASC"
    }
]
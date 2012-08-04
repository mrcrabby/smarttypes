

    @classmethod
    def mk_tag_clouds(cls, reduction_id, postgres_handle):
        print "starting community_wordcounts loop"
        community_wordcounts = {}
        all_words = set()
        for community in cls.get_all(reduction_id, postgres_handle):
            community_wordcounts[community.index] = (community, collections.defaultdict(int))
            for score, user in community.top_users(num_users=25):
                if not user.description:
                    continue
                regex = re.compile(r'[%s\s]+' % re.escape(string.punctuation))
                user_words = set()
                user.description = '' if not user.description else user.description
                user.location_name = '' if not user.location_name else user.location_name
                loc_desc = '%s %s' % (user.description.strip(), user.location_name.strip())
                for word in regex.split(loc_desc):
                    word = string.lower(word)
                    if len(word) > 2 and word not in user_words:
                        user_words.add(word)
                        all_words.add(word)
                        community_wordcounts[community.index][1][word] += score
                        
        print "starting avg_wordcounts loop"            
        avg_wordcounts = {} #{word:avg}
        sum_words = []#[(sum,word)]
        for word in all_words:
            community_usage = []
            for community_index in community_wordcounts:
                community_usage.append(community_wordcounts[community_index][1][word])
            avg_wordcounts[word] = numpy.average(community_usage)
            sum_words.append((numpy.sum(community_usage), word))        
        
        print "starting delete stop words loop"
        for community_index in community_wordcounts:
            for word in text_parsing.STOPWORDS:
                if word in community_wordcounts[community_index][1]:
                    del community_wordcounts[community_index][1][word]     
                
        print "starting communities_unique_words loop"
        communities_unique_words = {} #{community_index:[(score, word)]}
        for community_index in community_wordcounts:
            communities_unique_words[community_index] = []
            for word, times_used in community_wordcounts[community_index][1].items():
                usage_diff = times_used - avg_wordcounts[word]
                communities_unique_words[community_index].append((usage_diff, word))
        
        print "starting save tag_cloud loop"
        for community_index, unique_scores in communities_unique_words.items():
            community = community_wordcounts[community_index][0]
            community.tag_cloud = [x[1] for x in heapq.nlargest(10, unique_scores)]
            community.save()
        
        return "All done!"
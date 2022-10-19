from redis import Redis


class Poll:
    redis = Redis(host='localhost', port=6379, db=0)

    @staticmethod
    def _get_next_poll_id():
        length = Poll.redis.get('poll:len')
        length = int(length) if length is not None else 0
        Poll.redis.set('poll:len', length + 1)
        return length + 1

    @staticmethod
    def create_poll(name, options):
        poll_id = Poll._get_next_poll_id()

        Poll.redis.set('poll:len', poll_id)
        Poll.redis.set(f'poll:{poll_id}:name', name)

        for option_id, name in enumerate(options):
            Poll.redis.set(f'poll:{poll_id}:option:{option_id + 1}:name', name)

        Poll.redis.set(f'poll:{poll_id}:options', len(options))

        return poll_id

    @staticmethod
    def vote_poll(poll_id, option_id, ip_address):
        option_length = int(Poll.redis.get(f'poll:{poll_id}:options'))

        is_member = False
        for local_id in range(1, option_length + 1):
            local_is_member = Poll.redis.sismember(f'poll:{poll_id}:option:{local_id}', ip_address)
            if local_is_member:
                is_member = True

        if not is_member:
            if int(option_id) > option_length:
                raise TypeError

            Poll.redis.sadd(f'poll:{poll_id}:option:{option_id}', ip_address)
            return True

        return False

    @staticmethod
    def stats_poll(poll_id):
        option_length = int(Poll.redis.get(f'poll:{poll_id}:options'))
        poll_name = Poll.redis.get(f'poll:{poll_id}:name').decode()

        options = []
        total = 0

        for option_id in range(1, option_length + 1):
            option_name = Poll.redis.get(f'poll:{poll_id}:option:{option_id}:name').decode()
            option_votes = Poll.redis.scard(f'poll:{poll_id}:option:{option_id}')

            options.append({
                'id': option_id,
                'name': option_name,
                'votes': option_votes
            })
            total += option_votes

        for option in options:
            percent = 0
            if option['votes']:
                percent = option['votes'] / total * 100

            option['percent'] = percent

        return {
            'id': poll_id,
            'name': poll_name,
            'options': options,
            'total': total
        }

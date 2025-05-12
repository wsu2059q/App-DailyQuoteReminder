class DFA:
    def __init__(self):
        self.ban_words_set = set()
        self.ban_words_list = list()
        self.ban_words_dict = dict()
        from .words import sensitive_words_content
        # 直接在代码中定义敏感词
        self.sensitive_words_content = sensitive_words_content

        self.get_words_from_string()

    # 从字符串中加载敏感词
    def get_words_from_string(self):
        lines = self.sensitive_words_content.strip().split('\n')
        for s in lines:
            s = s.strip()
            if len(s) == 0:
                continue
            if s not in self.ban_words_set:
                self.ban_words_set.add(s)
                self.ban_words_list.append(s)
        self.add_hash_dict(self.ban_words_list)

    # 以下方法保持不变
    def change_words(self, words_str):
        self.ban_words_list.clear()
        self.ban_words_dict.clear()
        self.ban_words_set.clear()
        self.sensitive_words_content = words_str
        self.get_words_from_string()

    def add_hash_dict(self, new_list):
        for x in new_list:
            self.add_new_word(x)

    def add_new_word(self, new_word):
        new_word = str(new_word)
        now_dict = self.ban_words_dict
        i = 0
        for x in new_word:
            if x not in now_dict:
                x = str(x)
                new_dict = dict()
                new_dict['is_end'] = False
                now_dict[x] = new_dict
                now_dict = new_dict
            else:
                now_dict = now_dict[x]
            if i == len(new_word) - 1:
                now_dict['is_end'] = True
            i += 1

    def find_illegal(self, _str):
        now_dict = self.ban_words_dict
        i = 0
        start_word = -1
        is_start = True
        while i < len(_str):
            if _str[i] not in now_dict:
                if is_start is True:
                    i += 1
                    continue
                i = start_word + 1
                start_word = -1
                is_start = True
                now_dict = self.ban_words_dict
            else:
                if is_start is True:
                    start_word = i
                    is_start = False
                now_dict = now_dict[_str[i]]
                if now_dict['is_end'] is True:
                    return start_word
                else:
                    i += 1
        return -1

    def exists(self, s):
        pos = self.find_illegal(s)
        return pos != -1

    def filter_words(self, filter_str, pos):
        now_dict = self.ban_words_dict
        end_str = 0
        for i in range(pos, len(filter_str)):
            if now_dict[filter_str[i]]['is_end'] is True:
                end_str = i
                break
            now_dict = now_dict[filter_str[i]]
        num = end_str - pos + 1
        return filter_str[:pos] + '*' * num + filter_str[end_str + 1:]

    def filter_all(self, s):
        pos_list = []
        ss = DFA.draw_words(s, pos_list)
        illegal_pos = self.find_illegal(ss)
        while illegal_pos != -1:
            ss = self.filter_words(ss, illegal_pos)
            illegal_pos = self.find_illegal(ss)
        i = 0
        while i < len(ss):
            if ss[i] == '*':
                start = pos_list[i]
                while i < len(ss) and ss[i] == '*':
                    i += 1
                i -= 1
                end = pos_list[i]
                num = end - start + 1
                s = s[:start] + '*' * num + s[end + 1:]
            i += 1
        return s

    @staticmethod
    def draw_words(_str, pos_list):
        ss = ""
        for i in range(len(_str)):
            if '\u4e00' <= _str[i] <= '\u9fa5' or '\u3400' <= _str[i] <= '\u4db5' or '\u0030' <= _str[i] <= '\u0039' \
                    or '\u0061' <= _str[i] <= '\u007a' or '\u0041' <= _str[i] <= '\u005a':
                ss += _str[i]
                pos_list.append(i)
        return ss
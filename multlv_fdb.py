
class GradQueues:

    def __init__(self):
        self.level_size = 1
        self.queue_size = 15
        self.judge_num = [0]
        self.queue_list = [[]]

    def put(self, filelist):
        for file in filelist:
            if self.judge_num[-1] == self.queue_size:
                self.judge_num.append(0)
                self.queue_list.append([])
            insert_file = file
            for temp in range(len(self.queue_list)):
                insert_file = self.insert(insert_file, self.queue_list[temp], temp)
                if insert_file == 1:
                    break

    def insert(self, f, queue, temp):
        # 队列未装满, 直接将文件放入该队列
        if self.judge_num[temp] < self.queue_size:
            queue.append(self.file(f[0], f[1]))
            self.judge_num[temp] += 1
            queue.sort(key=lambda file: file.tag, reverse=True)
            # print([x.tag for x in queue])
            return 1
        # 队列已满, 若f的tag比其中最小tag还要大, 就插入该队列，并返回被替换的文件放入后续队列中
        if f[0] > queue[-1].tag:
            ret_file = queue[-1]
            queue[-1] = self.file(f[0], f[1])
            queue.sort(key=lambda file: file.tag, reverse=True)
            # print([x.tag for x in queue])
            return [ret_file.tag, ret_file.ciphertext]
        # 队列已满, f的tag比其中最小tag还要小, 直接返回f进入下一层队列
        return f

    class file:
        def __init__(self,  tag, ciphertext):
            self.ciphertext = ciphertext
            self.tag = tag

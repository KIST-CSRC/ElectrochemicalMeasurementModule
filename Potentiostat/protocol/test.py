start = 200000
end = 0.1
points_per_decade = 6
i = 0
value_list = []

while start/pow(10, (i/points_per_decade)) > 0.1:
    i += 1
    value = start/pow(10,(i/points_per_decade))
    print(value)
    value_list.append(value)

print(len(value_list))
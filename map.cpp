#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <cstdlib>
#include <ctime>
#include <cmath>

class Map {
public:
    struct Room {
        int x, y, w, h;
        
        bool intersect(const Room &r) const {
            return !(r.x >= (x + w) || x >= (r.x + r.w) || r.y >= (y + h) || y >= (r.y + r.h));
        }
    };

    struct Point {
        int x, y, cost;
        
        bool operator==(const Point &p) const {
            return x == p.x && y == p.y;
        }
        
        bool operator<(const Point &p) const {
            return cost > p.cost; // Для использования в std::priority_queue
        }
    };

    Map(int width, int height): m_width(width), m_height(height) {
        m_data.resize(width * height, 0);
    }

    void generate(int roomsCount);
    void generatePassage(const Point &start, const Point &finish);
    void generateWalls();
    void printMap() const;

    const std::vector<Room>& getRooms() const { return m_rooms; } // Публичный метод доступа

private:
    int m_width, m_height;
    std::vector<int> m_data;
    std::vector<Room> m_rooms;

    int calcCost(const Point &current, const Point &finish) const;
};

void Map::generate(int roomsCount) {
    m_rooms.clear();
    
    for (int i = 0; i < roomsCount; ++i) {
        for (int j = 0; j < 1000; ++j) {
            const int w = 10 + rand() % 31;
            const int h = 10 + rand() % 31;
            const Room room = {3 + rand() % (m_width - w - 6), 3 + rand() % (m_height - h - 6), w, h};
            
            auto intersect = std::find_if(m_rooms.begin(), m_rooms.end(), [&room](const Room &r){
                return room.intersect(r);
            });
            
            if (intersect == m_rooms.end()) {
                m_rooms.push_back(room);
                break;
            }
        }
    }
    
    m_data.assign(m_width * m_height, 0);
    for (const Room &room : m_rooms) {
        for (int x = 0; x < room.w; ++x) {
            for (int y = 0; y < room.h; ++y) {
                m_data[(room.x + x) + (room.y + y) * m_width] = 1;
            }
        }
    }
}

int Map::calcCost(const Point &current, const Point &finish) const {
    int dx = std::abs(current.x - finish.x);
    int dy = std::abs(current.y - finish.y);
    return dx + dy;
}

void Map::generatePassage(const Point &start, const Point &finish) {
    std::vector<int> parents(m_width * m_height, -1);
    std::priority_queue<Point> active;
    active.push(start);
    
    static const int directions[4][2] = {{1,0}, {0,1}, {-1,0}, {0,-1}};
    
    while (!active.empty()) {
        const Point point = active.top();
        active.pop();
        
        if (point == finish)
            break;
        
        for (int i = 0; i < 4; ++i) {
            Point p = {point.x + directions[i][0], point.y + directions[i][1], 0};
            if (p.x < 0 || p.y < 0 || p.x >= m_width || p.y >= m_height)
                continue;
            
            if (parents[p.x + p.y * m_width] < 0) {
                p.cost = calcCost(p, finish);
                active.push(p);
                parents[p.x + p.y * m_width] = i;
            }
        }
    }
    
    Point point = finish;
    while (!(point == start)) {
        m_data[point.x + point.y * m_width] = 1;
        const int direction = parents[point.x + point.y * m_width];
        if (direction == -1)
            break;
        point.x -= directions[direction][0];
        point.y -= directions[direction][1];
    }
}

void Map::generateWalls() {
    static const int offsets[8][2] = {
        {-1,-1}, { 0,-1}, { 1,-1}, { 1, 0},
        { 1, 1}, { 0, 1}, {-1, 1}, {-1, 0},
    };
    
    for (int x = 1; x < m_width - 1; ++x) {
        for (int y = 1; y < m_height - 1; ++y) {
            if (m_data[x + y * m_width] == 0) {
                for (int i = 0; i < 8; ++i) {
                    if (m_data[(x + offsets[i][0]) + (y + offsets[i][1]) * m_width] == 1) {
                        m_data[x + y * m_width] = 2;
                        break;
                    }
                }
            }
        }
    }
}

void Map::printMap() const {
    for (int y = 0; y < m_height; ++y) {
        for (int x = 0; x < m_width; ++x) {
            switch (m_data[x + y * m_width]) {
                case 0: std::cout << '.'; break;
                case 1: std::cout << ' '; break;
                case 2: std::cout << '#'; break;
            }
        }
        std::cout << '\n';
    }
}

int main() {
    srand(static_cast<unsigned>(time(0)));
    
    Map map(40, 20);
    map.generate(10);
    const auto& rooms = map.getRooms(); // Получаем список комнат

    for (size_t i = 0; i < rooms.size() - 1; ++i) {
        Map::Point start = {rooms[i].x + rooms[i].w / 2, rooms[i].y + rooms[i].h / 2, 0};
        Map::Point finish = {rooms[i + 1].x + rooms[i + 1].w / 2, rooms[i + 1].y + rooms[i + 1].h / 2, 0};
        map.generatePassage(start, finish);
    }
    map.generateWalls();
    map.printMap();
    
    return 0;
}

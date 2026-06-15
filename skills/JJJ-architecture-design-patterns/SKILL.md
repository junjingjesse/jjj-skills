---
name: JJJ-architecture-design-patterns
description: "设计模式技能，23种GoF模式分类整理与SOLID原则应用"
trigger: ["设计模式","GoF","ingleton","工厂方法","观察者","策略"]
---

# 设计模式技能 (Design Patterns)

## 快速开始

当用户触发此技能时，直接说：

**请描述你的设计问题，我来帮你匹配适用的设计模式。**

然后等待用户输入。

---

## 设计模式概述

### 什么是设计模式

设计模式是解决软件中**重复出现设计问题**的实际可行方案，由专家反复验证得出。

- **可复用 (Reusable)**：可应用于多个不同项目
- **灵活 (Flexible)**：解决方案可适应不同场景
- **经验性 (Proven)**：源于实际工业软件实践

### GoF 23种设计模式

《Design Patterns: Elements of Reusable Object-Oriented Software》
作者：Gamma, Helm, Johnson, Vlissides（Gang of Four）

| 类别 | 关注点 | 模式数量 |
|------|--------|----------|
| **创建型 (Creational)** | 对象创建机制 | 5 |
| **结构型 (Structural)** | 对象组合与结构 | 7 |
| **行为型 (Behavioral)** | 对象间交互与职责 | 11 |

---

## 创建型模式 (Creational Patterns)

### 核心思想
关注如何创建对象，而非对象如何使用。

---

### 1. 单例模式 (Singleton)

**意图**：确保一个类只有一个实例，并提供全局访问点

**问题场景**：
- 移动应用用户偏好类：存储界面颜色、卡牌背面设计等，存在多个实例会造成数据冲突
- 打印队列：多个打印队列对象导致任务顺序混乱
- 设备驱动：需要单一实例管理硬件资源

**实现步骤**：
1. 将构造函数设为 `private`
2. 声明 `private static uniqueInstance`
3. 提供 `public static getInstance()` 方法

**标准实现**：
```java
public class Singleton {
    private static Singleton uniqueInstance;

    private Singleton() {}  // 禁止外部实例化

    public static Singleton getInstance() {
        if (uniqueInstance == null) {
            uniqueInstance = new Singleton();
        }
        return uniqueInstance;
    }
}
```

**懒创建 (Lazy Initialization)**：
- 在第一次调用 getInstance() 时才创建实例
- 优势：节约内存、提升启动效率

**多线程问题**：
- 风险：多线程同时调用可能创建多个实例
- 解决：synchronized 同步、双重检查锁定、静态初始化

**记忆口诀**：VIP票券系统，一张票只能被一人持有

---

### 2. 工厂方法模式 (Factory Method)

**意图**：定义创建对象的接口，让子类决定实例化哪个类

**核心思想**：
- 客户端依赖抽象（接口）而非具体实现
- 子类决定具体产品类型
- 遵循"开闭原则"——对扩展开放，对修改封闭

**KnifeStore 案例**：

```
抽象创建者：KnifeStore
    - orderKnife() [通用逻辑]
    - createKnife() [抽象方法]

具体创建者：BudgetKnifeStore
    - createKnife() → 返回 BudgetChefsKnife

具体创建者：QualityKnifeStore
    - createKnife() → 返回 QualityChefsKnife
```

**客户端代码**：
```java
KnifeStore store = new QualityKnifeStore();
Knife knife = store.createKnife();  // 客户端只知道 Knife，不知道具体类型
knife.sharpen();
knife.polish();
```

**工厂对象 vs 工厂方法**：
| 类型 | 说明 |
|------|------|
| 工厂对象 | 独立对象负责创建，客户端调用工厂对象 |
| 工厂方法 | 抽象类内定义方法，子类实现决定创建什么 |

**记忆口诀**：工厂管创建，客户端管业务

---

### 3. 抽象工厂模式 (Abstract Factory)

**意图**：提供一个创建一系列相关对象的接口，而无需指定具体类

**适用场景**：需要创建对象家族（相关对象组）

**结构**：
```
AbstractFactory
    - createProductA()
    - createProductB()

ConcreteFactory1
    - createProductA() → ProductA1
    - createProductB() → ProductB1

ConcreteFactory2
    - createProductA() → ProductA2
    - createProductB() → ProductB2
```

---

### 4. 原型模式 (Prototype)

**意图**：通过克隆现有对象创建新对象，而非从头创建

**适用场景**：
- 对象创建成本高（如游戏角色、复杂图形）
- 对象种类繁多，难以分类

**实现方式**：
```java
public interface Prototype {
    Prototype clone();
}

public class Dog implements Prototype {
    String name;
    int age;

    @Override
    public Prototype clone() {
        Dog copy = new Dog();
        copy.name = this.name;
        copy.age = this.age;
        return copy;
    }
}
```

---

### 5. 建造者模式 (Builder)

**意图**：分步骤构建复杂对象

**适用场景**：
- 构造函数参数过多
- 对象构建复杂，需要可变组合

**示例**：
```java
public class User {
    private String firstName;
    private String lastName;
    private int age;
    private String address;
    // ... 更多字段
}

public class UserBuilder {
    private User user = new User();

    public UserBuilder firstName(String fn) {
        user.setFirstName(fn);
        return this;
    }

    public UserBuilder lastName(String ln) {
        user.setLastName(ln);
        return this;
    }

    public User build() {
        return user;
    }
}

// 使用
User user = new UserBuilder()
    .firstName("John")
    .lastName("Doe")
    .age(30)
    .build();
```

---

## 结构型模式 (Structural Patterns)

### 核心思想
关注对象间关系及继承结构

---

### 6. 适配器模式 (Adapter)

**意图**：将不兼容的接口转换为客户端期望的接口

**问题场景**：
```
WebClient 发送任意对象
WebService 只接受 Json
直接交互会报错
```

**解决方案**：
```
Client → Target Interface (WebRequester) → Adapter → Adaptee (WebService)
```

**组成**：
| 角色 | 说明 |
|------|------|
| Client | 需要使用第三方库的代码 |
| Target Interface | 客户端期望的接口 |
| Adapter | 实现目标接口，转换请求 |
| Adaptee | 第三方库，接口不兼容 |

**Java实现**：
```java
// Target Interface
public interface WebRequester {
    void sendMessage(Object msg);
}

// Adaptee (第三方系统)
public class WebService {
    public void sendJson(Json obj) { /* ... */ }
}

// Adapter
public class WebAdapter implements WebRequester {
    private WebService webService;

    public void sendMessage(Object msg) {
        Json json = convertToJson(msg);  // 转换逻辑
        webService.sendJson(json);
    }
}
```

**记忆口诀**：接口不合别慌张，Adapter来帮忙

---

### 7. 外观模式 (Facade)

**意图**：提供一个统一接口，简化复杂子系统的访问

**类比**：餐厅服务员处理订单，客户不接触厨房

**问题场景**：
```
Without Facade:
Customer → CheckingAccount, SavingAccount, InvestmentAccount (直接接触多个类)

With Facade:
Customer → BankService (Facade) → 内部封装多个账户类
```

**实现**：
```java
public class BankService {
    private CheckingAccount checking;
    private SavingAccount saving;
    private InvestmentAccount investment;

    public BankService() {
        checking = new CheckingAccount();
        saving = new SavingAccount();
        investment = new InvestmentAccount();
    }

    public void deposit(String type, double amount) {
        if (type.equals("checking")) {
            checking.deposit(amount);
        } else if (type.equals("saving")) {
            saving.deposit(amount);
        }
        // ...
    }
}
```

**核心**：不增加系统功能，仅作为访问入口

---

### 8. 代理模式 (Proxy)

**意图**：为真实对象提供替身，控制对它的访问

**三种类型**：

| 类型 | 用途 | 示例 |
|------|------|------|
| **虚拟代理** | 延迟创建资源密集型对象 | 图片懒加载、网页加载 |
| **保护代理** | 控制访问权限 | 根据角色检查权限 |
| **远程代理** | 操作远程对象 | Google Docs |

**结构**：
```
Client → Subject Interface → Proxy → RealSubject
```

**订单分发系统案例**：
```java
public interface IOrder {
    void process(Order order);
}

public class Warehouse implements IOrder {
    public void process(Order order) {
        // 处理订单
    }
}

public class OrderFulfillment implements IOrder {
    private Warehouse warehouse;

    public void process(Order order) {
        // 代理：先检查库存
        if (checkInventory(order)) {
            warehouse.process(order);
        } else {
            reject(order);
        }
    }
}
```

**记忆口诀**：代理替身来站岗，访问控制我在行

---

### 9. 装饰器模式 (Decorator)

**意图**：动态为对象添加行为，使用聚合代替继承

**问题**：继承是静态的，每种组合需子类 → 类爆炸

**解决方案**：聚合代替继承，运行时动态组合

**咖啡案例**：
```
基础组件：黑咖啡 (ConcreteComponent)
装饰器：牛奶、糖、巧克力 (ConcreteDecorator)
```

**执行顺序**（递归调用）：
```
CoffeeWithMilk.withSugar().display()
  → SugarDecorator.display()
    → MilkDecorator.display()
      → BlackCoffee.display()
```

**Java实现**：
```java
public interface Coffee {
    String getDescription();
    double getCost();
}

public class BlackCoffee implements Coffee {
    public String getDescription() { return "黑咖啡"; }
    public double getCost() { return 10.0; }
}

public abstract class CoffeeDecorator implements Coffee {
    protected Coffee coffee;  // 聚合基础对象
    public CoffeeDecorator(Coffee coffee) { this.coffee = coffee; }
}

public class MilkDecorator extends CoffeeDecorator {
    public MilkDecorator(Coffee coffee) { super(coffee); }

    public String getDescription() {
        return coffee.getDescription() + " + 牛奶";
    }
    public double getCost() {
        return coffee.getCost() + 3.0;
    }
}

// 使用
Coffee coffee = new MilkDecorator(new BlackCoffee());
```

**优势**：避免类爆炸，运行时动态组合

---

### 10. 组合模式 (Composite)

**意图**：将对象组织成树状结构，统一处理单个对象与组合对象

**组成**：
| 角色 | 说明 |
|------|------|
| Component | 统一接口，定义共同行为 |
| Composite | 可包含子对象（Leaf或其他Composite） |
| Leaf | 终端节点，不能包含子对象 |

**建筑案例**：
```
Building (Composite)
    └── Floor (Composite)
          ├── Room (Leaf)
          └── Room (Leaf)
```

**Java实现**：
```java
public interface FileSystem {
    String getName();
    int getSize();
    void display(String indent);
}

public class File implements FileSystem {
    private String name;
    private int size;
    // getters, display()

    public void display(String indent) {
        System.out.println(indent + name + " (" + size + "KB)");
    }
}

public class Folder implements FileSystem {
    private String name;
    private List<FileSystem> children = new ArrayList<>();

    public void add(FileSystem fs) { children.add(fs); }

    public void display(String indent) {
        System.out.println(indent + name + "/");
        for (FileSystem fs : children) {
            fs.display(indent + "  ");
        }
    }
}
```

**记忆口诀**：树状组合终端叶，统一接口操作它

---

### 11. 桥接模式 (Bridge)

**意图**：分离抽象部分与实现部分，使两者可独立变化

**结构**：
```
Abstraction → Implementor
    ↓              ↓
RefinedAbstraction → ConcreteImplementor
```

---

### 12. 亨元模式 (Flyweight)

**意图**：共享细粒度对象，减少内存

**适用场景**：大量相似对象的创建

---

## 行为型模式 (Behavioral Patterns)

### 核心思想
关注对象间协作与职责分配

---

### 13. 模板方法模式 (Template Method)

**意图**：在超类中定义算法框架，可变步骤延迟到子类

**核心**：
- 模板方法用 `final` 修饰，防止覆盖
- 子类实现抽象方法（可变步骤）

**PastaDish 案例**：
```java
public abstract class PastaDish {
    // 模板方法 final，防止覆盖
    public final void makeRecipe() {
        boilWater();
        addPasta();      // 子类实现
        addSauce();      // 子类实现
        addGarnish();    // 子类实现
    }

    private void boilWater() {
        System.out.println("烧水...");
    }

    protected abstract void addPasta();
    protected abstract void addSauce();
    protected abstract void addGarnish();
}

public class SpaghettiMeatballs extends PastaDish {
    protected void addPasta() { System.out.println("加意面"); }
    protected void addSauce() { System.out.println("加肉酱"); }
    protected void addGarnish() { System.out.println("加肉丸"); }
}
```

**记忆口诀**：模板固定框架，子类添花步

---

### 14. 责任链模式 (Chain of Responsibility)

**意图**：将请求沿对象链传递，发送者无需关心处理者

**流程**：
```
请求 → Handler1 → Handler2 → Handler3 → (处理/链尾)
```

**医疗转诊案例**：
```
普通医生 → 专科医生 → 专家
  ↓          ↓         ↓
能处理?     能处理?   最终处理
  ↓          ↓
转下一个   转下一个
```

**邮件过滤案例**：
```java
public interface Handler {
    void setNext(Handler handler);
    void handle(Email email);
}

public class SpamHandler implements Handler {
    private Handler next;
    public void setNext(Handler h) { next = h; }

    public void handle(Email email) {
        if (email.isSpam()) {
            email.moveToSpamFolder();
        } else if (next != null) {
            next.handle(email);
        }
    }
}
```

**记忆口诀**：请求沿链走，处理谁不求

---

### 15. 状态模式 (State)

**意图**：对象行为随状态动态改变，将状态逻辑封装在独立类中

**核心**：避免长条件语句（if-else/switch）

**自动售货机案例**：
```
状态：Idle, HasOneDollar, OutOfStock
事件：insertDollar, ejectMoney, dispense

转换：
Idle --insertDollar--> HasOneDollar
HasOneDollar --dispense--> Idle (库存>0) 或 OutOfStock (库存=0)
HasOneDollar --ejectMoney--> Idle
```

**实现**：
```java
public interface State {
    void insertDollar(VendingMachine vm);
    void ejectMoney(VendingMachine vm);
    void dispense(VendingMachine vm);
}

public class IdleState implements State {
    public void insertDollar(VendingMachine vm) {
        vm.setState(new HasOneDollarState());
    }
    // ... 其他方法
}

public class VendingMachine {
    private State state = new IdleState();
    public void setState(State s) { state = s; }

    public void insertDollar() { state.insertDollar(this); }
    public void dispense() { state.dispense(this); }
}
```

**状态模式 vs 策略模式**：
| 模式 | 说明 |
|------|------|
| 状态模式 | 状态自动触发行为变化 |
| 策略模式 | 客户端主动选择算法 |

---

### 16. 命令模式 (Command)

**意图**：将请求封装为对象，支持撤销/重做、队列调度

**组成**：
| 角色 | 说明 |
|------|------|
| Sender | 发起请求 |
| Receiver | 执行实际操作 |
| Command | 封装请求 |
| Invoker | 调用命令 |

**撤销/重做机制**：
```
执行 → History List
撤销 → Redo List
新执行 → 清空Redo List
```

**文本编辑器案例**：
```java
public interface Command {
    void execute();
    void undo();
}

public class PasteCommand implements Command {
    private Editor editor;
    private String pasted;

    public PasteCommand(Editor editor, String text) {
        this.editor = editor;
        this.pasted = text;
    }

    public void execute() {
        editor.insert(pasted);
    }

    public void undo() {
        editor.delete(pasted.length());
    }
}

public class CommandManager {
    private Stack<Command> history = new Stack<>();
    private Stack<Command> redo = new Stack<>();

    public void execute(Command cmd) {
        cmd.execute();
        history.push(cmd);
        redo.clear();
    }

    public void undo() {
        if (!history.isEmpty()) {
            Command cmd = history.pop();
            cmd.undo();
            redo.push(cmd);
        }
    }
}
```

---

### 17. 观察者模式 (Observer)

**意图**：对象状态变化时自动通知依赖对象

**组成**：
| 角色 | 说明 |
|------|------|
| Subject | 维护观察者列表，提供注册/注销/通知 |
| Observer | 定义update()方法 |

**在MVC中的应用**：
```
Model (Subject) → notifyObservers() → View (Observer)
```

**博客订阅案例**：
```java
public interface Observer {
    void update(String message);
}

public class Blog {
    private List<Observer> subscribers = new ArrayList<>();

    public void subscribe(Observer o) { subscribers.add(o); }
    public void unsubscribe(Observer o) { subscribers.remove(o); }

    public void postArticle(String title) {
        // 发布文章
        notifySubscribers("新文章: " + title);
    }

    private void notifySubscribers(String message) {
        for (Observer o : subscribers) {
            o.update(message);
        }
    }
}

public class Subscriber implements Observer {
    public void update(String message) {
        System.out.println("收到通知: " + message);
    }
}
```

---

### 18. 迭代器模式 (Iterator)

**意图**：提供顺序访问集合元素的方法，不暴露集合内部

---

### 19. 中介者模式 (Mediator)

**意图**：用一个中介对象封装对象间交互

**问题**：对象间直接通信 → 紧耦合

**解决**：通过中介者协调

**智能家居案例**：
```
Without Mediator:
闹钟 → 门 → 咖啡机 → 窗帘 (直接通信，复杂难维护)

With Mediator:
闹钟 → HomeController (Mediator) → 统一协调
```

---

### 20. 备忘录模式 (Memento)

**意图**：保存对象状态，后续恢复

**组成**：
| 角色 | 说明 |
|------|------|
| Originator | 创建备忘录 |
| Memento | 存储状态 |
| Caretaker | 管理备忘录 |

---

### 21. 解释器模式 (Interpreter)

**意图**：定义语法表示和解释器

---

### 22. 访问者模式 (Visitor)

**意图**：分离数据结构和操作

---

### 23. 策略模式 (Strategy)

**意图**：定义一系列算法，使其可互换

**支付案例**：
```java
public interface PaymentStrategy {
    void pay(double amount);
}

public class CreditCardPayment implements PaymentStrategy {
    public void pay(double amount) {
        System.out.println("信用卡支付: $" + amount);
    }
}

public class PayPalPayment implements PaymentStrategy {
    public void pay(double amount) {
        System.out.println("PayPal支付: $" + amount);
    }
}

public class ShoppingCart {
    private PaymentStrategy payment;

    public void checkout(double amount) {
        payment.pay(amount);
    }
}
```

---

## SOLID原则

| 原则 | 全称 | 核心思想 |
|------|------|----------|
| **SRP** | 单一职责原则 | 一个类只有一个变化原因 |
| **OCP** | 开放/封闭原则 | 对扩展开放，对修改封闭 |
| **LSP** | Liskov替换原则 | 子类可替换父类 |
| **ISP** | 接口隔离原则 | 类不依赖不使用的方法 |
| **DIP** | 依赖倒置原则 | 高层依赖抽象，低层实现抽象 |

---

### 开放/封闭原则 (OCP)

**定义**：类应对扩展开放，对修改封闭

**实现**：
- 继承（子类扩展功能）
- 多态（不同实现替换）

**违反示例**：Stack extends Vector
- Stack获得了不该有的列表操作

---

### Liskov替换原则 (LSP)

**定义**：子类型必须能替换其父类型而不改变行为

**子类型限制**：
1. 子类不能强化前置条件（如添加更多条件判断是否调用方法）
2. 子类不能弱化后置条件
3. 子类必须保持父类的不变条件
4. 子类不能修改父类的不可变属性

**违反示例**：
- `Whale extends Animal`：Animal有walk()，Whale无法实现
- `Square extends Rectangle`：Rectangle允许独立设置width/height，Square不行

---

### 接口隔离原则 (ISP)

**定义**：类不应依赖它不使用的方法

**超市收银系统案例**：
```
ICashier (scanItems, acceptPayment, dispenseChange)
    ↑
--------|--------
HumanCashier  SelfServeMachine
(+ clockIn,   (只需ICashier)
 takeBreak)
```

---

### 依赖倒置原则 (DIP)

**定义**：
- 高层模块依赖抽象
- 低层模块实现抽象

```
Client → Interface ← ConcreteA
                ← ConcreteB
```

---

### 迪米特法则 (Law of Demeter)

**核心**：方法只与本地对象通信

**允许调用**：
1. 同一对象的方法
2. 方法参数对象的方法
3. 方法内新建对象的方法
4. 类实例变量对象的方法

**禁止**：`driver.car.engine.start()` —— 穿透调用

---

## 代码异味 (Code Smells)

### 重构时机
- 添加新功能时
- 代码审查发现问题时

### 第一类代码异味

| 类型 | 表现 | 解决方案 |
|------|------|----------|
| **重复代码** | 相似代码多处出现 | 提取方法，D.R.Y.原则 |
| **过长方法** | 方法超过50行 | 拆分为小方法 |
| **大类** | 类承担过多职责 | 分离关注点 |
| **长参数列表** | 参数超过3个 | 参数对象封装 |
| **数据类** | 只有getter/setter | 封装行为 |

### 第二类代码异味

| 类型 | 表现 | 解决方案 |
|------|------|----------|
| **发散性修改** | 类因多种原因需修改 | 分离职责 |
| **霰弹手术** | 修改一处需改多处 | 方法局部化 |
| **功能嫉妒** | 方法过度依赖其他类 | 方法迁移 |
| **消息链** | 链式调用 a.getB().getC() | 遵循LoD原则 |
| **原始类型依赖** | 用int/String代替对象 | 封装为类 |
| **switch滥用** | 大量if-else/switch | 多态替代 |
| **过度设计** | 为未来可能设计 | Just-in-Time |
| **拒绝继承** | 子类继承了不需要的方法 | 组合替代继承 |
| **不当亲密** | 两个类相互过度依赖 | 单向依赖 |

### 重构核心原则

| 原则 | 说明 |
|------|------|
| **D.R.Y.** | Don't Repeat Yourself |
| **封装** | 封装变化点 |
| **分离关注点** | 一个类只做一件事 |
| **Just-in-Time** | 按需设计，不过度设计 |

---

## 模式应用决策树

```
你需要创建对象吗?
├─ 只需要一个实例 → Singleton
├─ 复杂对象创建 → Builder
├─ 子类决定创建什么 → Factory Method
├─ 对象家族 → Abstract Factory
└─ 克隆已有对象 → Prototype

你需要组合对象吗?
├─ 树状结构统一处理 → Composite
├─ 动态添加行为 → Decorator
├─ 简化复杂接口 → Facade
└─ 控制访问 → Proxy

你需要协调对象交互?
├─ 请求沿链传递 → Chain of Responsibility
├─ 状态相关行为 → State
├─ 命令封装撤销/重做 → Command
├─ 状态变化通知 → Observer
└─ 算法可互换 → Strategy
```

---

## 常见问题

### Q: 什么时候用继承 vs 组合？
- 需要复用代码、行为固定 → 继承
- 需要运行时动态组合 → 组合
- 避免继承的紧耦合 → 优先组合

### Q: 如何避免类爆炸？
- 使用装饰器模式动态组合行为
- 避免每种组合都创建子类

### Q: 什么时候用设计模式？
- 遇到重复设计问题时
- 需要与团队统一设计词汇时
- 不确定时优先考虑简单设计

### Q: 为什么单例被过度使用？
- 全局状态导致隐藏依赖
- 难以测试
- 紧耦合
- 多线程问题复杂

### Q: 策略模式和状态模式的区别？
- 策略模式：客户端主动选择算法
- 状态模式：对象行为随内部状态自动变化

---

## 记忆口诀汇总

| 模式 | 口诀 |
|------|------|
| Singleton | VIP票券系统，保证唯一全局访问 |
| Factory | 工厂管创建，客户端管业务 |
| Adapter | 接口不合别慌张，Adapter来帮忙 |
| Facade | 外观只做门面，复杂藏里面 |
| Proxy | 代理替身来站岗，访问控制我在行 |
| Decorator | 底层基础不可动，装饰递增叠加行 |
| Composite | 树状组合终端叶，统一接口操作它 |
| Template | 模板固定框架，子类添花步 |
| Chain | 请求沿链走，处理谁不求 |
| State | 状态知己，行为随变 |
| Command | 命令封装请求，撤销重做轻松 |
| Observer | 主题通知一声令下，观察者列表各自更新 |
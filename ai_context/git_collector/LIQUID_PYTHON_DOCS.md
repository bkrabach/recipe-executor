# jg-rp/liquid/docs

[git-collector-data]

**URL:** https://github.com/jg-rp/liquid/docs  
**Date:** 4/26/2025, 8:32:57 AM  
**Files:** 6  

=== File: docs/environment.md ===
# Liquid environments

Template parsing and rendering behavior is configured using an instance of [`Environment`](api/environment.md). Once configured, you'd parse templates with [`Environment.from_string()`](api/environment.md#liquid.Environment.from_string) or [`Environment.get_template()`](api/environment.md#liquid.Environment.get_template), both of which return an instance of [`BoundTemplate`](api/template.md).

## The default environment

The default environment, `liquid.DEFAULT_ENVIRONMENT`, and an instance of `Environment` without any arguments are equivalent to the following `Environment` subclass and constructor arguments.

```python
from liquid import BoundTemplate
from liquid import DictLoader
from liquid import Environment
from liquid import Mode
from liquid import Undefined
from liquid import builtin


class MyLiquidEnvironment(Environment):
    context_depth_limit = 30
    loop_iteration_limit = None
    local_namespace_limit = None
    output_stream_limit = None
    template_class = BoundTemplate
    suppress_blank_control_flow_blocks = True
    shorthand_indexes = False
    string_sequences = False
    string_first_and_last = False
    logical_not_operator = False
    logical_parentheses = False
    ternary_expressions = False
    keyword_assignment = False

    def setup_tags_and_filters(self):
        builtin.register(self)


env = MyLiquidEnvironment(
    autoescape=False,
    comment_end_string="#}",
    comment_start_string="{#",
    extra=False,
    globals=None,
    loader=DictLoader({}),
    statement_end_string=r"}}",
    statement_start_string=r"{{",
    strict_filters=True,
    tag_end_string=r"%}",
    tag_start_string=r"{%",
    template_comments=False,
    tolerance=Mode.STRICT,
    undefined=Undefined,
)
```

## Managing tags and filters

[`liquid.builtin.register()`](api/builtin.md#liquid.builtin.register) registers all the default tags and filters with the environment. You are encouraged to override `setup_tags_and_filters()` in your `Environment` subclasses to add optional or custom tags and filters, remove unwanted default tags and filters, and possibly replace default implementation with your own.

It's also OK to manipulate [`Environment.tags`](api/environment.md#liquid.Environment.tags) and [`Environment.filters`](api/environment.md#liquid.Environment.filters) directly after an `Environment` instance has been created. They are just dictionaries mapping tag names to instances of [`Tag`](api/tag.md) and filter names to callables, respectively.

```python
from liquid import Environment

env = Environment()
del env.tags["include"]
```

### Extra tags and filters

Python Liquid includes some [extra tags](optional_tags.md) and [extra filters](optional_filters.md) that are not enabled by default. If you want to enable them all, pass `extra=True` when constructing a Liquid [`Environment`](api/environment.md).

```python
from liquid import Environment

env = Environment(extra=True)
print(env.render("{{ 100457.99 | money }}"))
# $100,457.99
```

## Managing global variables

By default, global template variables attached to instances of [`BoundTemplate`](api/template.md) take priority over global template variables attached to an `Environment`. You can change this priority or otherwise manipulate the `globals` dictionary for a `BoundTemplate` by overriding [`Environment.make_globals()`](api/environment.md#liquid.Environment.make_globals).

Also see [Render context data](render_context.md).

```python
from typing import Mapping
from liquid import Environment

class MyLiquidEnvironment(Environment):

    def make_globals(
        self,
        globals: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        """Combine environment globals with template globals."""
        if globals:
            # Template globals take priority over environment globals.
            return {**self.globals, **globals}
        return dict(self.globals)
```

## Tolerance

Templates are parsed and rendered in strict mode by default. Where syntax and render-time type errors raise an exception as soon as possible. You can change the error tolerance mode with the `tolerance` argument to [`Environment`](api/environment.md).

Available modes are `Mode.STRICT`, `Mode.WARN` and `Mode.LAX`.

```python
from liquid import Environment
from liquid import FileSystemLoader
from liquid import Mode

env = Environment(
    loader=FileSystemLoader("templates/"),
    tolerance=Mode.LAX,
)
```

## HTML auto escape

When `autoescape` is `True`, [render context variables](render_context.md) will be automatically escaped to produce HTML-safe strings on output.

You can be explicitly mark strings as _safe_ by wrapping them in `Markup()` and [drops](variables_and_drops.md) can implement the [special `__html__()` method](variables_and_drops.md#__html__).

```python
from markupsafe import Markup
from liquid import Environment

env = Environment(autoescape=True)
template = env.from_string("<p>Hello, {{ you }}</p>")
print(template.render(you=Markup("<em>World!</em>")))
```

## Resource limits

For deployments where template authors are untrusted, you can set limits on some resources to avoid malicious templates from consuming too much memory or too many CPU cycles. Limits are set by subclassing [`Environment`](api/environment.md) and setting some class attributes.

```python
from liquid import Environment

class MyEnvironment(Environment):
    context_depth_limit = 30
    local_namespace_limit = 2000
    loop_iteration_limit = 1000
    output_stream_limit = 15000


env = MyEnvironment()

template = env.from_string("""\
{% for x in (1..1000000) %}
{% for y in (1..1000000) %}
    {{ x }},{{ y }}
{% endfor %}
{% endfor %}
""")

template.render()
# liquid.exceptions.LoopIterationLimitError: loop iteration limit reached
```

### Context depth limit

[`context_depth_limit`](api/environment.md#liquid.Environment.context_depth_limit) is the maximum number of times a render context can be extended or wrapped before a `ContextDepthError` is raised. This helps us guard against recursive use of the `include` and `render` tags. The default context depth limit is 30.

```python
from liquid import Environment
from liquid import DictLoader

env = Environment(
    loader=DictLoader(
        {
            "foo": "{% render 'bar' %}",
            "bar": "{% render 'foo' %}",
        }
    )
)

template = env.from_string("{% render 'foo' %}")
template.render()
# liquid.exceptions.ContextDepthError: maximum context depth reached, possible recursive render
#   -> '{% render 'bar' %}' 1:3
#   |
# 1 | {% render 'bar' %}
#   |    ^^^^^^ maximum context depth reached, possible recursive render
```

### Local Namespace Limit

[`local_namespace_limit`](api/environment.md#liquid.Environment.local_namespace_limit) is the maximum number of bytes (according to `sys.getsizeof()`) allowed in a template's local namespace, per render, before a `LocalNamespaceLimitError` exception is raised. Note that we only count the size of the local namespace values, not its keys.

The default `local_namespace_limit` is `None`, meaning there is no limit.

```python
from liquid import Environment

class MyEnvironment(Environment):
    local_namespace_limit = 50  # Very low, for demonstration purposes.

env = MyEnvironment()

template = env.from_string("""\
{% assign x = "Nunc est nulla, pellentesque ac dui id erat curae." %}
""")

template.render()
# liquid.exceptions.LocalNamespaceLimitError: local namespace limit reached
```

!!! warning

    [PyPy](https://doc.pypy.org/en/latest/cpython_differences.html) does not implement `sys.getsizeof`. Instead of a size in bytes, when run with PyPy, `local_namespace_limit` will degrade to being the number of distinct values in a template's local namespace.

### Loop Iteration Limit

[`loop_iteration_limit`](api/environment.md#liquid.Environment.loop_iteration_limit) is the maximum number of loop iterations allowed before a `LoopIterationLimitError` is raised.

The default `loop_iteration_limit` is `None`, meaning there is no limit.

```python
from liquid import Environment

class MyEnvironment(Environment):
    loop_iteration_limit = 999


env = MyEnvironment()

template = env.from_string("""\
{% for x in (1..100) %}
{% for y in (1..100) %}
    {{ x }},{{ y }}
{% endfor %}
{% endfor %}
""")

template.render()
# liquid.exceptions.LoopIterationLimitError: loop iteration limit reached
```

Other built in tags that contribute to the loop iteration counter are `render`, `include` (when using their `{% render 'thing' for some.thing %}` syntax) and `tablerow`. If a partial template is rendered within a `for` loop, the loop counter is carried over to the render context of the partial template.

### Output Stream Limit

The maximum number of bytes that can be written to a template's output stream, per render, before an `OutputStreamLimitError` exception is raised. The default `output_stream_limit` is `None`, meaning there is no limit.

```python
from liquid import Environment

class MyEnvironment(Environment):
    output_stream_limit = 20  # Very low, for demonstration purposes.


env = MyEnvironment()

template = env.from_string("""\
{% if false %}
this is never rendered, so will not contribute the the output byte counter
{% endif %}
Hello, {{ you }}!
""")

template.render(you="World")
# '\nHello, World!\n'

template.render(you="something longer that exceeds our limit")
# liquid.exceptions.OutputStreamLimitError: output stream limit reached
```

## String sequences

By default, strings in Liquid can not be looped over with the `{% for %}` tag and characters in a string can not be selected by index.

Setting the `string_sequences` class attribute to `True` tells Python Liquid to treat strings as sequences, meaning we can loop over Unicode characters in a string or retrieve a Unicode "character" by its index.

## String first and last

Strings don't respond to the special `.first` and `.last` properties by default. Set `string_first_and_last` to `True` to enable `.first` and `.last` for strings.

## Logical not operator

The logical `not` operator is disabled by default. Set the `logical_not_operator` class attribute to `True` to enable `not` inside `{% if %}`, `{% unless %}` and ternary expressions.

## Logical parentheses

By default, terms in `{% if %}` tag expressions can not be grouped to control precedence. Set the `logical_parentheses` class attribute to `True` to enable grouping terms with parentheses.

## Ternary expressions

Enable ternary expressions in output statements, assign tags and echo tags by setting the `ternary_expressions` class attribute to `True`.

```
{{ <expression> if <expression> else <expression> }}
```

Inline conditional expressions can be used as an alternative to the longer form [`{% if %}` tag](tag_reference.md#if).

```liquid
{{ "bar" if x.y == z else "baz" }}
```

Filters can be applied to either branch.

```liquid
{{ "bar" | upcase if x else "baz" | capitalize }}
```

Or applied to the result of the conditional expression as a whole using _tail filters_. Notice the double pipe symbol (`||`).

```liquid
{{ "bar" if x else "baz" || upcase | append: "!" }}
```

## Keyword assignment

By default, named arguments must separated names from values with a colon (`:`). Set the `keyword_assignment` class attribute to `True` to allow equals (`=`) or a colon between names and their values.

## What's next?

See [loading templates](loading_templates.md) for more information about configuring a template loader and [undefined variables](variables_and_drops.md#undefined-variables) for information about managing undefined variables.


=== File: docs/filter_reference.md ===
All the filters described here are enabled by default in Python Liquid2.

## abs

```
<number> | abs
```

Return the absolute value of a number. Works on integers, floats and string representations of integers or floats.

```liquid2
{{ -42 | abs }}
{{ 7.5 | abs }}
{{ '42.0' | abs }}
```

```plain title="output"
42
7.5
42.0
```

Given a value that can't be cast to an integer or float, `0` will be returned.

```liquid2
{{ 'hello' | abs }}
{{ nosuchthing | abs }}
```

```plain title="output"
0
0
```

## append

```
<string> | append: <string>
```

Return the input value concatenated with the argument value.

```liquid2
{{ 'Hello, ' | append: 'World!' }}
```

```plain title="output"
Hello, World!
```

If either the input value or argument are not a string, they will be coerced to a string before concatenation.

```liquid2
{% assign a_number = 7.5 -%}
{{ 42 | append: a_number }}
{{ nosuchthing | append: 'World!' }}
```

```plain title="output"
427.5
World!
```

## at_least

```
<number> | at_least: <number>
```

Return the maximum of the filter's input value and its argument. If either input value or argument are string representations of an integer or float, they will be cast to an integer or float prior to comparison.

```liquid2
{{ -5.1 | at_least: 8 }}
{{ 8 | at_least: '5' }}
```

```plain title="output"
8
8
```

If either input value or argument can not be cast to an integer or float, `0` will be used instead.

```liquid2
{{ "hello" | at_least: 2 }}
{{ "hello" | at_least: -2 }}
{{ -1 | at_least: "abc" }}
```

```plain title="output"
2
0
0
```

## at_most

```
<number> | at_most: <number>
```

Return the minimum of the filter's input value and its argument. If either input value or argument are string representations of an integer or float, they will be cast to an integer or float prior to comparison.

```liquid2
{{ 5 | at_most: 8 }}
{{ '8' | at_most: 5 }}
```

```plain title="output"
5
5
```

If either input value or argument can not be cast to an integer or float, `0` will be used instead.

```liquid2
{{ "hello" | at_most: 2 }}
{{ "hello" | at_most: -2 }}
{{ -1 | at_most: "abc" }}
```

```plain title="output"
0
-2
-1
```

## capitalize

```
<string> | capitalize
```

Return the input string with the first character in upper case and the rest lowercase.

```liquid2
{{ 'heLLO, World!' | capitalize }}
```

```plain title="output"
Hello, world!
```

If the input value is not a string, it will be converted to a string.

```liquid2
{{ 42 | capitalize }}
```

```plain title="output"
42
```

## ceil

```
<number> | ceil
```

Round the input value up to the nearest whole number. The input value will be converted to a number if it is not an integer or float.

```liquid2
{{ 5.1 | ceil }}
{{ 5.0 | ceil }}
{{ 5 | ceil }}
{{ '5.4' | ceil }}
```

```plain title="output"
6
5
5
5
```

If the input is undefined or can't be converted to a number, `0` is returned.

```liquid2
{{ 'hello' | ceil }}
{{ nosuchthing | ceil }}
```

```plain title="output"
0
0
```

## compact

```
<array> | compact[: <string>]
```

Remove `nil`/`null` (or `None` in Python) values from an array-like object. If given, the argument should be the name of a property that exists on each item (hash, dict etc.) in the array-like sequence.

For example, ff `pages` is an array of objects, some of which have a `category` property:

```json title="data"
{
  "pages": [
    { "category": "business" },
    { "category": "celebrities" },
    {},
    { "category": "lifestyle" },
    { "category": "sports" },
    {},
    { "category": "technology" }
  ]
}
```

Without `compact`, iterating those categories will include `nil`/`null` values.

```liquid2
{% assign categories = pages | map: "category" -%}

{% for category in categories -%}
- {{ category }}
{%- endfor %}
```

```plain title="output"
- business
- celebrities
-
- lifestyle
- sports
-
- technology
```

With `compact`, we can remove those missing categories before the loop.

```liquid2
{% assign categories = pages | map: "category" | compact %}

{% for category in categories %}
- {{ category }}
{% endfor %}
```

```plain title="output"
- business
- celebrities
- lifestyle
- sports
- technology
```

Using the optional argument to `compact`, we could avoid using `map` and create an array of pages with a `category` property, rather than an array of categories.

```liquid2
{% assign pages_with_category = pages | compact: "category" %}

{% for page in pages_with_category %}
- {{ page.category }}
{% endfor %}
```

```plain title="output"
- business
- celebrities
- lifestyle
- sports
- technology
```

## concat

```
<array> | concat: <array>
```

Create a new array by joining one array-like object with another.

```liquid2
{% assign fruits = "apples, oranges, peaches" | split: ", " %}
{% assign vegetables = "carrots, turnips, potatoes" | split: ", " %}

{% assign everything = fruits | concat: vegetables %}

{% for item in everything %}
- {{ item }}
{% endfor %}
```

```plain title="output"
- apples
- oranges
- peaches
- carrots
- turnips
- potatoes
```

If the input value is not array-like, it will be converted to an array. No conversion is attempted for the argument value.

```liquid2
{% assign fruits = "apples, oranges, peaches" | split: ", " -%}
{% assign things = "hello" | concat: fruits -%}

{% for item in things -%}
- {{ item }}
{% endfor %}
```

```plain title="output"
- h
- e
- l
- l
- o
- apples
- oranges
- peaches
```

If the input is a nested array, it will be flattened before concatenation. The argument is not flattened.

```json title="data"
{
  "a": [
    ["a", "x"],
    ["b", ["y", ["z"]]]
  ],
  "b": ["c", "d"]
}
```

```liquid2
{{ a | concat: b | join: '#' }}
```

```plain title="output"
a#x#b#y#z#c#d
```

## date

```
<datetime> | date: <string>
```

Format a date and/or time according the the given format string. The input can be a string, in which case the string will be parsed as a date/time before formatting.

!!! warning

    Python Liquid uses [dateutil](https://dateutil.readthedocs.io/en/stable/) for parsing strings to `datetimes`, and `strftime` for formatting. There are likely to be some inconsistencies between this and Ruby Liquid's [Time.parse](https://ruby-doc.org/stdlib-3.0.3/libdoc/time/rdoc/Time.html#method-c-parse) equivalent parsing and formatting of dates and times.

    In general, Python Liquid will raise an exception if the input value can not be converted to a date and/or time. Whereas Ruby Liquid will usually return something without erroring.

```liquid2
{{ "March 14, 2016" | date: "%b %d, %y" }}
```

```plain title="output"
Mar 14, 16
```

The special `'now'` or `'today'` input values can be used to get the current timestamp. `'today'` is an alias for `'now'`. Both include time information.

```liquid2
{{ "now" | date: "%Y-%m-%d %H:%M" }}
```

```plain title="output"
2021-12-02 10:17
```

If the input is undefined, an empty string is returned.

```liquid2
{{ nosuchthing | date: "%Y-%m-%d %H:%M" }}
```

```plain title="output"

```

## default

```
<expression> | default[: <object>[, allow_false:<bool>]]
```

Return a default value if the input is undefined, `nil`/`null`, `false` or empty, or return the input unchanged otherwise.

```liquid2
{{ product_price | default: 2.99 }}

{%- assign product_price = "" %}
{{ product_price | default: 2.99 }}

{%- assign product_price = 4.99 %}
{{ product_price | default: 2.99 }}
```

```plain title="output"
2.99
2.99
4.99
```

If the optional `allow_false` argument is `true`, an input of `false` will not return the default. `allow_false` defaults to `false`.

```liquid2
{% assign product_reduced = false -%}
{{ product_reduced | default: true, allow_false: true }}
```

```plain title="output"
false
```

If no argument is given, the default value will be an empty string.

```liquid2
{{ product_price | default }}
```

```plain title="output"

```

Empty strings, arrays and objects all cause the default value to be returned. `0` does not.

```liquid2
{{ "" | default: "hello" }}
{{ 0 | default: 99 }}
```

```plain title="output"
hello
0
```

## divided_by

```
<number> | divided_by: <number>
```

Divide a number by another number. The result is rounded down to the nearest integer if the divisor is an integer.

```liquid2
{{ 16 | divided_by: 4 }}
{{ 5 | divided_by: 3 }}
```

```plain title="output"
4
1
```

If you divide by a float, the result will be a float.

```liquid2
{{ 20 | divided_by: 7 }}
{{ 20 | divided_by: 7.0 }}
```

```plain title="output"
2
2.857142857142857
```

If either the input or argument are not an integer or float, Liquid will try to convert them to an integer or float. If the input can't be converted, `0` will be used instead. If the argument can't be converted, an exception is raised.

```liquid2
{{ "20" | divided_by: "7" }}
{{ "hello" | divided_by: 2 }}
```

```plain title="output"
2
0
```

## downcase

```
<string> | downcase
```

Return the input string with all characters in lowercase.

```liquid2
{{ 'Hello, World!' | downcase }}
```

```plain title="output"
hello, world!
```

If the input is not a string, Liquid will convert it to a string before forcing characters to lowercase.

```liquid2
{{ 5 | downcase }}
```

```plain title="output"
5
```

If the input is undefined, an empty string is returned.

## escape

```
<string> | escape
```

Return the input string with characters `&`, `<` and `>` converted to HTML-safe sequences.

```liquid2
{{ "Have you read 'James & the Giant Peach'?" | escape }}
```

```plain title="output"
Have you read &#39;James &amp; the Giant Peach&#39;?
```

## escape_once

```
<string> | escape_once
```

Return the input string with characters `&`, `<` and `>` converted to HTML-safe sequences while preserving existing HTML escape sequences.

```liquid2
{{ "Have you read 'James &amp; the Giant Peach'?" | escape_once }}
```

```plain title="output"
Have you read &#39;James &amp; the Giant Peach&#39;?
```

## find

```
<array> | find: <string>[, <object>]
```

Return the first item in the input array that contains a property, given as the first argument, equal to the value given as the second argument. If no such item exists, `null` is returned.

In this example we select the first page in the "Programming" category.

```json title="data"
{
  "pages": [
    {
      "id": 1,
      "title": "Introduction to Cooking",
      "category": "Cooking",
      "tags": ["recipes", "beginner", "cooking techniques"]
    },
    {
      "id": 2,
      "title": "Top 10 Travel Destinations in Europe",
      "category": "Travel",
      "tags": ["Europe", "destinations", "travel tips"]
    },
    {
      "id": 3,
      "title": "Mastering JavaScript",
      "category": "Programming",
      "tags": ["JavaScript", "web development", "coding"]
    }
  ]
}
```

```liquid2
{% assign page = pages | find: 'category', 'Programming' %}
{{ page.title }}
```

```plain title="output"
Mastering JavaScript
```

## find_index

Return the index of the first item in the input array that contains a property, given as the first argument, equal to the value given as the second argument. If no such item exists, `null` is returned.

In this example we find the index for the first page in the "Programming" category.

```json title="data"
{
  "pages": [
    {
      "id": 1,
      "title": "Introduction to Cooking",
      "category": "Cooking",
      "tags": ["recipes", "beginner", "cooking techniques"]
    },
    {
      "id": 2,
      "title": "Top 10 Travel Destinations in Europe",
      "category": "Travel",
      "tags": ["Europe", "destinations", "travel tips"]
    },
    {
      "id": 3,
      "title": "Mastering JavaScript",
      "category": "Programming",
      "tags": ["JavaScript", "web development", "coding"]
    }
  ]
}
```

```liquid2
{% assign index = pages | find_index: 'category', 'Programming' %}
{{ pages[index].title }}
```

```plain title="output"
Mastering JavaScript
```

## first

```
<sequence> | first
```

Return the first item of the input sequence. The input could be array-like or a mapping, but not a string.

```liquid2
{{ "Ground control to Major Tom." | split: " " | first }}
```

```plain title="output"
Ground
```

If the input sequence is undefined, empty or not a sequence, `nil` is returned.

## floor

```
<number> | floor
```

Return the input down to the nearest whole number. Liquid tries to convert the input to a number before the filter is applied.

```liquid2
{{ 1.2 | floor }}
{{ 2.0 | floor }}
{{ 183.357 | floor }}
{{ -5.4 | floor }}
{{ "3.5" | floor }}
```

```plain title="output"
1
2
183
-6
3
```

If the input can't be converted to a number, `0` is returned.

## has

```
<array> | has: <string>[, <object>]
```

Return `true` if the input array contains an object with a property identified by the first argument that is equal to the object given as the second argument. `false` is returned if none of the items in the input array contain such a property/value.

In this example we test to see if any pages are in the "Programming" category.

```json title="data"
{
  "pages": [
    {
      "id": 1,
      "title": "Introduction to Cooking",
      "category": "Cooking",
      "tags": ["recipes", "beginner", "cooking techniques"]
    },
    {
      "id": 2,
      "title": "Top 10 Travel Destinations in Europe",
      "category": "Travel",
      "tags": ["Europe", "destinations", "travel tips"]
    },
    {
      "id": 3,
      "title": "Mastering JavaScript",
      "category": "Programming",
      "tags": ["JavaScript", "web development", "coding"]
    }
  ]
}
```

```liquid2
{% assign has_programming_page = pages | has: 'category', 'Programming' %}
{{ has_programming_page }}
```

```plain title="output"
true
```

## join

```
<array> | join[: <string>]
```

Return the items in the input array as a single string, separated by the argument string. If the
input is not an array, Liquid will convert it to one. If input array items are not strings, they
will be converted to strings before joining.

```liquid2
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}

{{ beatles | join: " and " }}
```

```plain title="output"
John and Paul and George and Ringo
```

If an argument string is not given, it defaults to a single space.

```liquid2
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}

{{ beatles | join }}
```

```plain title="output"
John Paul George Ringo
```

## last

```
<array> | last
```

Return the last item in the array-like input.

```liquid2
{{ "Ground control to Major Tom." | split: " " | last }}
```

```plain title="output"
Tom.
```

If the input is undefined, empty, string or a number, `nil` will be returned.

## lstrip

```
<string> | lstrip
```

Return the input string with all leading whitespace removed. If the input is not a string, it will
be converted to a string before stripping whitespace.

```liquid2
{{ "          So much room for activities          " | lstrip }}!
```

```plain title="output"
So much room for activities          !
```

## map

```
<array> | map: <string | lambda expression>
```

Extract properties from an array of objects into a new array.

For example, if `pages` is an array of objects with a `category` property:

```json title="data"
{
  "pages": [
    { "category": "business" },
    { "category": "celebrities" },
    { "category": "lifestyle" },
    { "category": "sports" },
    { "category": "technology" }
  ]
}
```

```liquid2
{% assign categories = pages | map: "category" -%}

{% for category in categories -%}
- {{ category }}
{%- endfor %}
```

```plain title="output"
- business
- celebrities
- lifestyle
- sports
- technology
```

## minus

```
<number> | minus: <number>
```

Return the result of subtracting one number from another. If either the input or argument are not a number, Liquid will try to convert them to a number. If that conversion fails, `0` is used instead.

```liquid2
{{ 4 | minus: 2 }}
{{ "16" | minus: 4 }}
{{ 183.357 | minus: 12.2 }}
{{ "hello" | minus: 10 }}
```

```plain title="output"
2
12
171.157
-10
```

## modulo

```
<number> | modulo: <number>
```

Return the remainder from the division of the input by the argument.

```liquid2
{{ 3 | modulo: 2 }}
{{ "24" | modulo: "7" }}
{{ 183.357 | modulo: 12 }}
```

```plain title="output"
1
3
3.357
```

If either the input or argument are not an integer or float, Liquid will try to convert them to an
integer or float. If the input can't be converted, `0` will be used instead. If the argument can't
be converted, an exception is raised.

## newline_to_br

```
<string> | newline_to_br
```

Return the input string with `\n` and `\r\n` replaced with `<br />\n`.

```liquid2
{% capture string_with_newlines %}
Hello
there
{% endcapture %}

{{ string_with_newlines | newline_to_br }}
```

```plain title="output"


<br />
Hello<br />
there<br />

```

## plus

```
<number> | plus: <number>
```

Return the result of adding one number to another. If either the input or argument are not a number, Liquid will try to convert them to a number. If that conversion fails, `0` is used instead.

```liquid2
{{ 4 | plus: 2 }}
{{ "16" | plus: "4" }}
{{ 183.357 | plus: 12 }}
```

```plain title="output"
6
20
195.357
```

## prepend

```
<string> | prepend: <string>
```

Return the argument concatenated with the filter input.

```liquid2
{{ "apples, oranges, and bananas" | prepend: "Some fruit: " }}
```

```plain title="output"
Some fruit: apples, oranges, and bananas
```

If either the input value or argument are not a string, they will be coerced to a string before
concatenation.

```liquid2
{% assign a_number = 7.5 -%}
{{ 42 | prepend: a_number }}
{{ nosuchthing | prepend: 'World!' }}
```

```plain title="output"
7.542
World!
```

## reject

```
<array> | reject: <string>[, <object>]
```

Return a copy of the input array including only those objects that have a property, named with the first argument, **that is not equal to** a value, given as the second argument. If a second argument is not given, only elements with the named property that are falsy will be included.

```json title="data"
{
  "products": [
    { "title": "Vacuum", "type": "house", "available": true },
    { "title": "Spatula", "type": "kitchen", "available": false },
    { "title": "Television", "type": "lounge", "available": true },
    { "title": "Garlic press", "type": "kitchen", "available": true }
  ]
}
```

```liquid2
All products:
{% for product in products -%}
- {{ product.title }}
{% endfor %}

{%- assign kitchen_products = products | reject: "type", "kitchen" -%}

Non kitchen products:
{% for product in kitchen_products -%}
- {{ product.title }}
{% endfor %}

{%- assign unavailable_products = products | reject: "available" -%}

Unavailable products:
{% for product in unavailable_products -%}
- {{ product.title }}
{% endfor %}
```

```plain title="output"
All products:
- Vacuum
- Spatula
- Television
- Garlic press
Non kitchen products:
- Vacuum
- Television
Unavailable products:
- Spatula
```

## remove

```
<string> | remove: <string>
```

Return the input with all occurrences of the argument string removed.

```liquid2
{{ "I strained to see the train through the rain" | remove: "rain" }}
```

```plain title="output"
I sted to see the t through the
```

If either the filter input or argument are not a string, they will be coerced to a string before
substring removal.

## remove_first

```
<string> | remove_first: <string>
```

Return a copy of the input string with the first occurrence of the argument string removed.

```liquid2
{{ "I strained to see the train through the rain" | remove_first: "rain" }}
```

```plain title="output"
I sted to see the train through the rain
```

If either the filter input or argument are not a string, they will be coerced to a string before substring removal.

## remove_last

```
<string> | remove_last: <string>
```

Return a copy of the input string with the last occurrence of the argument string removed.

```liquid2
{{ "I strained to see the train through the rain" | remove_last: "rain" }}
```

```plain title="output"
I strained to see the train through the
```

If either the filter input or argument are not a string, they will be coerced to a string before substring removal.

## replace

```
<string> | replace: <string>[, <string>]
```

Return the input with all occurrences of the first argument replaced with the second argument. If
the second argument is omitted, it will default to an empty string, making `replace` behave like
`remove`.

```liquid2
{{ "Take my protein pills and put my helmet on" | replace: "my", "your" }}
```

```plain title="output"
Take your protein pills and put your helmet on
```

If either the filter input or argument are not a string, they will be coerced to a string before
replacement.

## replace_first

```
<string> | replace_first: <string>[, <string>]
```

Return a copy of the input string with the first occurrence of the first argument replaced with the second argument. If the second argument is omitted, it will default to an empty string, making `replace_first` behave like `remove_first`.

```liquid2
{{ "Take my protein pills and put my helmet on" | replace_first: "my", "your" }}
```

```plain title="output"
Take your protein pills and put my helmet on
```

If either the filter input or argument are not a string, they will be coerced to a string before replacement.

## replace_last

```
<string> | replace_last: <string>, <string>
```

Return a copy of the input string with the last occurrence of the first argument replaced with the second argument.

```liquid2
{{ "Take my protein pills and put my helmet on" | replace_first: "my", "your" }}
```

```plain title="output"
Take my protein pills and put your helmet on
```

If either the filter input or argument are not a string, they will be coerced to a string before replacement.

## reverse

```
<array> | reverse
```

Return a copy of the input array with the items in reverse order. If the filter input is a string, `reverse` will return the string unchanged.

```liquid2
{% assign my_array = "apples, oranges, peaches, plums" | split: ", " -%}

{{ my_array | reverse | join: ", " }}
```

```plain title="output"
plums, peaches, oranges, apples
```

## round

```
<number> | round[: <number>]
```

Return the input number rounded to the given number of decimal places. The number of digits defaults to `0`.

```liquid2
{{ 1.2 | round }}
{{ 2.7 | round }}
{{ 183.357 | round: 2 }}
```

```plain title="output"
1
3
183.36
```

If either the filter input or its optional argument are not an integer or float, they will be converted to an integer or float before rounding.

## rstrip

```
<string> | rstrip
```

Return the input string with all trailing whitespace removed. If the input is not a string, it will be converted to a string before stripping whitespace.

```liquid2
{{ "          So much room for activities          " | rstrip }}!
```

```plain title="output"
          So much room for activities!
```

## safe

```
<string> | safe
```

Return the input string marked as safe to use in an HTML or XML document. If the filter input is not a string, it will be converted to an HTML-safe string.

With auto-escape enabled and the following global variables:

```json title="data"
{
  "username": "Sally",
  "greeting": "</p><script>alert('XSS!');</script>"
}
```

```liquid2 title="template"
<p>{{ greeting }}, {{ username }}</p>
<p>{{ greeting | safe }}, {{ username }}</p>
```

```html title="output"
<p>&lt;/p&gt;&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;, Sally</p>
<p></p><script>alert('XSS!');</script>, Sally</p>
```

## size

```
<object> | size
```

Return the size of the input object. Works on strings, arrays and hashes.

```liquid2
{{ "Ground control to Major Tom." | size }}
{{ "apples, oranges, peaches, plums" | split: ", " | size }}
```

```plain title="output"
28
4
```

## slice

```
<sequence> | slice: <int>[, <int>]
```

Return a substring or subsequence of the input string or array. The first argument is the zero-based start index. The second, optional argument is the length of the substring or sequence, which defaults to `1`.

```liquid2
{{ "Liquid" | slice: 0 }}
{{ "Liquid" | slice: 2 }}
{{ "Liquid" | slice: 2, 5 }}
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}
{{ beatles | slice: 1, 2 | join: " " }}
```

```plain title="output"
L
q
quid
Paul George
```

If the first argument is negative, the start index is counted from the end of the sequence.

```liquid2
{{ "Liquid" | slice: -3 }}
{{ "Liquid" | slice: -3, 2 }}
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}
{{ beatles | slice: -2, 2 | join: " " }}
```

```plain title="output"
u
ui
George Ringo
```

## sort

````
<array> | sort[: <string>]
``

Return a copy of the input array with its elements sorted.

```liquid
{% assign my_array = "zebra, octopus, giraffe, Sally Snake" | split: ", " -%}
{{ my_array | sort | join: ", " }}
````

```plain title="output"
Sally Snake, giraffe, octopus, zebra
```

The optional argument is a sort key. If given, it should be the name of a property and the filter's input should be an array of objects.

```json title="data"
{
  "collection": {
    "products": [
      { "title": "A Shoe", "price": "9.95" },
      { "title": "A Tie", "price": "0.50" },
      { "title": "A Hat", "price": "2.50" }
    ]
  }
}
```

```liquid2 title="template"
{% assign products_by_price = collection.products | sort: "price" -%}
{% for product in products_by_price %}
  <h4>{{ product.title }}</h4>
{% endfor %}
```

```plain title="output"
<h4>A Tie</h4>
<h4>A Hat</h4>
<h4>A Shoe</h4>
```

## sort_natural

```
<array> | sort_natural[: <string>]
```

Return a copy of the input array with its elements sorted case-insensitively. Array items will be compared by their string representations, forced to lowercase.

```liquid2
{% assign my_array = "zebra, octopus, giraffe, Sally Snake" | split: ", " -%}
{{ my_array | sort_natural | join: ", " }}
```

```plain title="output"
giraffe, octopus, Sally Snake, zebra
```

The optional argument is a sort key. If given, it should be the name of a property and the filter's input should be an array of objects. Array elements are compared using the lowercase string representation of that property.

```json title="data"
{
  "collection": {
    "products": [
      { "title": "A Shoe", "company": "Cool Shoes" },
      { "title": "A Tie", "company": "alpha Ties" },
      { "title": "A Hat", "company": "Beta Hats" }
    ]
  }
}
```

```liquid2 title="template"
{% assign products_by_company = collection.products | sort_natural: "company" %}
{% for product in products_by_company %}
  <h4>{{ product.title }}</h4>
{% endfor %}
```

```plain title="output"
<h4>A Tie</h4>
<h4>A Hat</h4>
<h4>A Shoe</h4>
```

## split

```
<string> | split: <string>
```

Return an array of strings that are the input string split on the filter's argument string.

```liquid2
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}

{% for member in beatles %}
  {{- member }}
{% endfor %}
```

```plain title="output"
John
Paul
George
Ringo
```

If the argument is undefined or an empty string, the input will be split at every character.

```liquid2
{{ "Hello there" | split: nosuchthing | join: "#" }}
```

```plain title="output"
H#e#l#l#o# #t#h#e#r#e
```

## strip

```
<string> | strip
```

Return the input string with all leading and trailing whitespace removed. If the input is not a string, it will be converted to a string before stripping whitespace.

```liquid2
{{ "          So much room for activities          " | strip }}!
```

```plain title="output"
So much room for activities!
```

## strip_html

```
<string> | strip_html
```

Return the input string with all HTML tags removed.

```liquid2
{{ "Have <em>you</em> read <strong>Ulysses</strong>?" | strip_html }}
```

```plain title="output"
Have you read Ulysses?
```

## strip_newlines

```
<string> | strip_newlines
```

Return the input string with `\n` and `\r\n` removed.

```liquid2
{% capture string_with_newlines %}
Hello
there
{% endcapture -%}

{{ string_with_newlines | strip_newlines }}
```

```plain title="output"
Hellothere
```

## sum

```
<array> | sum[: <string>]
```

Return the sum of all numeric elements in an array.

```liquid2
{% assign array = '1,2,3' | split: ',' -%}
{{ array | sum }}
```

```plain title="output"
6
```

If the optional string argument is given, it is assumed that array items are hash/dict/mapping-like, and the argument should be the name of a property/key. The values at `array[property]` will be summed.

## times

```
<number> | times: <number>
```

Return the product of the input number and the argument. If either the input or argument are not a number, Liquid will try to convert them to a number. If that conversion fails, `0` is used instead.

```liquid2
{{ 3 | times: 2 }}
{{ "24" | times: "7" }}
{{ 183.357 | times: 12 }}
```

```plain title="output"
6
168
2200.284
```

## truncate

```
<string> | truncate[: <integer>[, <string>]]
```

Return a truncated version of the input string. The first argument, length, defaults to `50`. The second argument defaults to an ellipsis (`...`).

If the length of the input string is less than the given length (first argument), the input string will be truncated to `length` minus the length of the second argument, with the second argument appended.

```liquid2
{{ "Ground control to Major Tom." | truncate: 20 }}
{{ "Ground control to Major Tom." | truncate: 25, ", and so on" }}
{{ "Ground control to Major Tom." | truncate: 20, "" }}
```

```plain title="output"
Ground control to...
Ground control, and so on
Ground control to Ma
```

## truncatewords

```
<string> | truncatewords[: <integer>[, <string>]]
```

Return the input string truncated to the specified number of words, with the second argument appended. The number of words (first argument) defaults to `15`. The second argument defaults to an ellipsis (`...`).

If the input string already has fewer than the given number of words, it is returned unchanged.

```liquid2
{{ "Ground control to Major Tom." | truncatewords: 3 }}
{{ "Ground control to Major Tom." | truncatewords: 3, "--" }}
{{ "Ground control to Major Tom." | truncatewords: 3, "" }}
```

```plain title="output"
Ground control to...
Ground control to--
Ground control to
```

## uniq

```
<array> | uniq[: <string>]
```

Return a copy of the input array with duplicate elements removed.

```liquid2
{% assign my_array = "ants, bugs, bees, bugs, ants" | split: ", " -%}
{{ my_array | uniq | join: ", " }}
```

```plain title="output"
ants, bugs, bees
```

If an argument is given, it should be the name of a property and the filter's input should be an array of objects.

```json title="data"
{
  "collection": {
    "products": [
      { "title": "A Shoe", "company": "Cool Shoes" },
      { "title": "A Tie", "company": "alpha Ties" },
      { "title": "Another Tie", "company": "alpha Ties" },
      { "title": "A Hat", "company": "Beta Hats" }
    ]
  }
}
```

```liquid2 title="template"
{% assign one_product_from_each_company = collections.products | uniq: "company" -%}
{% for product in one_product_from_each_company -%}
  - product.title
{% endfor %}
```

```plain title="output"
- A Shoe
- A Tie
- A Hat
```

## upcase

```
<string> | upcase
```

Return the input string with all characters in uppercase.

```liquid2
{{ 'Hello, World!' | upcase }}
```

```plain title="output"
HELLO, WORLD!
```

## url_decode

```
<string> | url_decode
```

Return the input string with `%xx` escapes replaced with their single-character equivalents. Also replaces `'+'` with `' '`.

```liquid2
{{ "My+email+address+is+bob%40example.com%21" | url_decode }}
```

```plain title="output"
My email address is bob@example.com!
```

## url_encode

```
<string> | url_encode
```

Return the input string with URL reserved characters %-escaped. Also replaces `' '` with `'+'`.

```liquid2
{{ My email address is bob@example.com! | url_encode }}
```

```plain title="output"
My+email+address+is+bob%40example.com%21
```

## where

```
<array> | where: <string>[, <object>]
```

Return a copy of the input array including only those objects that have a property, named with the first argument, equal to a value, given as the second argument. If a second argument is not given, only elements with the named property that are truthy will be included.

```json title="data"
{
  "products": [
    { "title": "Vacuum", "type": "house", "available": true },
    { "title": "Spatula", "type": "kitchen", "available": false },
    { "title": "Television", "type": "lounge", "available": true },
    { "title": "Garlic press", "type": "kitchen", "available": true }
  ]
}
```

```liquid2
All products:
{% for product in products -%}
- {{ product.title }}
{% endfor %}

{%- assign kitchen_products = products | where: "type", "kitchen" -%}

Kitchen products:
{% for product in kitchen_products -%}
- {{ product.title }}
{% endfor %}

{%- assign available_products = products | where: "available" -%}

Available products:
{% for product in available_products -%}
- {{ product.title }}
{% endfor %}
```

```plain title="output"
All products:
- Vacuum
- Spatula
- Television
- Garlic press

Kitchen products:
- Spatula
- Garlic press

Available product:
- Vacuum
- Television
- Garlic press
```


=== File: docs/static_analysis.md ===
Instances of [`BoundTemplate`](api/template.md), as returned by [`parse()`](api/convenience.md#liquid.parse), [`from_string()`](api/environment.md#liquid.Environment.from_string) and [`get_template()`](api/environment.md#liquid.Environment.get_template), include several methods for inspecting a template's variable, tag a filter usage, without rendering the template.

By default, all of these methods will try to load and analyze [included](tag_reference.md#include), [rendered](tag_reference.md#render) and [extended](optional_tags.md#extends) templates too. Set the `include_partials` keyword only argument to `False` to disable automatic loading and analysis of partial/parent templates.

## Variables

[`variables()`](api/template.md#liquid.BoundTemplate.variables) and [`variables_async()`](api/template.md#liquid.BoundTemplate.variables_async) return a list of distinct variables used in the template, without [path segments](variables_and_drops.md#paths-to-variables). The list will include variables that are _local_ to the template, like those crated with `{% assign %}` and `{% capture %}`, or are in scope from `{% for %}` tags.

```python
from liquid import parse

source = """\
Hello, {{ you }}!
{% assign x = 'foo' | upcase %}

{% for ch in x %}
    - {{ ch }}
{% endfor %}

Goodbye, {{ you.first_name | capitalize }} {{ you.last_name }}
Goodbye, {{ you.first_name }} {{ you.last_name }}
"""

template = parse(source)
print(template.variables())
```

```plain title="output"
['you', 'x', 'ch']
```

## Variable paths

[`variable_paths()`](api/template.md#liquid.BoundTemplate.variable_paths) and [`variable_paths_async()`](api/template.md#liquid.BoundTemplate.variable_paths_async) return a list of variables used in the template, including all path segments. The list will include variables that are _local_ to the template, like those crated with `{% assign %}` and `{% capture %}`, or are in scope from `{% for %}` tags.

```python
# ... continued from above

print(template.variable_paths())
```

```plain title="output"
['you.first_name', 'you', 'you.last_name', 'x', 'ch']
```

## Variable segments

[`variable_segments()`](api/template.md#liquid.BoundTemplate.variable_segments) and [`variable_segments_async()`](api/template.md#liquid.BoundTemplate.variable_segments_async) return a list of variables used in the template, each as a list of segments. The list will include variables that are _local_ to the template, like those crated with `{% assign %}` and `{% capture %}`, or are in scope from `{% for %}` tags.

```python
# ... continued from above

print(template.variable_segments())
```

```plain title="output"
[
    ["you", "last_name"],
    ["you"],
    ["you", "first_name"],
    ["ch"],
    ["x"],
]
```

## Global variables

[`global_variables()`](api/template.md#liquid.BoundTemplate.global_variables) and [`global_variables_async()`](api/template.md#liquid.BoundTemplate.global_variables_async) return a list of variables used in the template, without path segments and excluding variables that are local to the template.

```python
# ... continued from above

print(template.global_variables())
```

```plain title="output"
['you']
```

## Global variable paths

[`global_variable_paths()`](api/template.md#liquid.BoundTemplate.global_variable_paths) and [`global_variable_paths_async()`](api/template.md#liquid.BoundTemplate.global_variable_paths_async) return a list of variables used in the template, with path segments and excluding variables that are local to the template.

```python
# ... continued from above

print(template.global_variable_paths())
```

```plain title="output"
['you', 'you.first_name', 'you.last_name']
```

## Global variable segments

[`global_variable_segments()`](api/template.md#liquid.BoundTemplate.global_variable_segments) and [`global_variable_segments_async()`](api/template.md#liquid.BoundTemplate.global_variable_segments_async) return a list of variables used in the template, each as a list of segments, excluding variables that are local to the template.

```python
# ... continued from above

print(template.global_variable_segments())
```

```plain title="output"
[
    ['you', 'last_name'],
    ['you', 'first_name'],
    ['you'],
]
```

## Filter names

[`filter_names()`](api/template.md#liquid.BoundTemplate.filter_names) and [`filter_names_async()`](api/template.md#liquid.BoundTemplate.filter_names_async) return names of filters used in the template.

```python
# ... continued from above

print(template.filter_names())
```

```plain title="output"
['upcase', 'capitalize']
```

## Tag names

[`tag_names()`](api/template.md#liquid.BoundTemplate.tag_names) and [`tag_names_async()`](api/template.md#liquid.BoundTemplate.tag_names_async) return the names of tags used in the template.

```python
# ... continued from above

print(template.tag_names())
```

```plain title="output"
['assign', 'for']
```

## Variable, tag and filter locations

[`analyze()`](api/template.md#liquid.BoundTemplate.analyze) and [`analyze_async()`](api/template.md#liquid.BoundTemplate.analyze_async) return an instance of [`TemplateAnalysis`](api/template.md#liquid.static_analysis.TemplateAnalysis). It contains all of the information provided by the methods described above, but includes the location of each variable, tag and filter, each of which can appear many times across many templates.


=== File: docs/syntax.md ===
Liquid is a template language, where source text (the template) contains placeholders for variables, conditional expressions for including or excluding blocks of text, and loops for repeating blocks of text. Plus other syntax for manipulating variables and combining multiple templates into a single output.

Output text is the result of _rendering_ a template given some data model. It is that data model that provides the variables and objects referenced in a template's expressions.

Liquid is most commonly used with HTML or Markdown, but can be used with any text-based content. Consider this example template.

```liquid2
<main>
  <h2>{{ page_heading | default: "Welcome to Our Benchmark Test" }}</h2>
  <p>{{ intro_text | default: "This is a dynamically generated page." }}</p>

  {% # About us section }
  <section>
    <h3>About Us</h3>
    {% if site_description %}
      <p>{{ site_description }}</p>
    {% endif %}
  <section>

  <section>
    <h3>Items List</h3>
    {% assign items_size = items | size %}
    {% if items_size > 0 %}
      {% for item in items %}
        <div class="item">
          <h4>{{ item.title | capitalize }}</h4>
          <p>{{ item.description | escape }}</p>
          <p>Price: {{ item.price | ceil }} USD</p>

          {% if item.price > 50 %}
            <p>This is a premium item.</p>
            {% else %}
            <p>This is a budget-friendly item.</p>
          {% endif %}
        </div>
      {% endfor %}
    {% else %}
      <p>No items are available at the moment.</p>
    {% endif %}
  </section>
</main>
```

## Output

`{{ site_description }}` and `{{ item.title | capitalize }}` are examples of [output statements](tag_reference.md#output). Expressions surrounded by double curly braces, `{{` and `}}`, will be evaluated and the result inserted into the output text.

## Filters

`capitalize` in `{{ item.title | capitalize }}` and `ceil` in `{{ item.price | ceil }}` are examples of [filters](tag_reference.md#filters). Filters modify the expression to their left prior to output or assignment.

## Tags

`{% if site_description %}`, `{% endif %}` and `{% assign items_size = items | size %}` are examples of [tags](tag_reference.md). After the start tag delimiter (`{%`) there must be a tag name. Everything up to the closing tag delimiter (`%}`) is the tags's expression.

Not all tags accept an expression, but all tag must have a name.

Together `{% if site_description %}` and `{% endif %}` form a _block tag_. Block tags have an opening tag, some Liquid in between, and an end tag. In the case of the [`if tag`](tag_reference.md#if), the block is only rendered if the tag's expression evaluates to true.

`{% assign items_size = items | size %}` is an _inline tag_. It does not have an _end tag_ and it does not output anything, although some inline tags do produce an output.

## Comments

`{% # About us section %}` is an example of a [comment](tag_reference.md#comments). Text between `{% #` and `%}` will not be parsed or rendered.

## Content

`<main>` and `\n    <h3>About Us</h3>` are examples of template content. That's anything not inside `{%` and `%}` or `{{` and `}}`. With the exception of whitespace control, template content is output unchanged.

## Whitespace control

By default, all whitespace immediately before and after a tag is preserved. This can result in a lot of unwanted whitespace.

```liquid2
<ul>
{% for x in (1..4) %}
  <li>{{ x }}</li>
{% endfor %}
</ul>
```

```plain title="output"
<ul>

  <li>1</li>

  <li>2</li>

  <li>3</li>

  <li>4</li>

</ul>
```

We can include a `-` at the start or end of a tag or output markup to strip preceding or trailing whitespace.

```liquid2
<ul>
{% for x in (1..4) -%}
  <li>{{ x }}</li>
{% endfor -%}
</ul>
```

```plain title="output"
<ul>
<li>1</li>
<li>2</li>
<li>3</li>
<li>4</li>
</ul>
```

!!! note

    Fine grained control over when to remove newlines vs indentation is not a standard feature of Liquid templates.


=== File: docs/tag_reference.md ===
All the tags described here are enabled by default in Python Liquid.

## Comments

Comments can be used to add documentation to your templates or "comment out" chunks of Liquid markup and text so that it wont be rendered.

### Block comments

```liquid2
{% comment %} ... {% endcomment %}
```

Block comments start with the `comment` tag and end with the `endcomment` tag. It is OK for comment text to contain matching `comment`/`endcomment` or `raw`/`endraw` pairs, but is a syntax error if `comment` or `raw` tags are unbalanced.

```liquid2
{% comment %}This is a comment{% endcomment %}
{% comment %}
    Comments can
    span
    multiple lines
{% endcomment %}
```

### Inline comments

```
{% # ... %}
```

An inline comment is a tag called `#`. Everything after the hash up to the end tag delimiter (`%}`) is comment text. Text can span multiple lines, but each line must start with a `#`.

```liquid2
{% # This is a comment %}
{%-
  # Comments can span multiple lines,
  # but every line must start with a hash.
-%}
```

Inside [liquid tags](#liquid), any line starting with a hash will be considered a comment.

```liquid2
{% liquid
  # This is a comment
  echo "Hello"
%}
```

## Output

```
{{ <expression> }}
```

An expression surrounded by double curly braces, `{{` and `}}`, is an _output statement_. When rendered, the expression will be evaluated and the result inserted into the output text.

In this example the expression is a variable, which will be resolved to a value and the value's string representation will output, but output statements can contain any primitive expression.

```liquid2
Hello, {{ you }}!
```

### Primitive expressions

| Primitive expression | Examples                                                      |
| -------------------- | ------------------------------------------------------------- |
| Boolean literal      | `true` or `false`                                             |
| Null literal         | `null` or `nil`                                               |
| Integer literal      | `123`                                                         |
| Float literal        | `1.23`                                                        |
| String literal       | `"Hello"` or `'Hello'`                                        |
| Range                | `(1..5)` or `(x..y)`                                          |
| A path to a variable | `foo` or `foo.bar` or `foo.bar[0]` or `foo["some thing"].bar` |

### Filters

```
{{ <expression> | <filter> [| <filter> ...] }}
```

Values can be modified prior to output using filters. Filters are applied to an expression using the pipe symbol (`|`), followed by the filter's name and, possibly, some filter arguments. Filter arguments appear after a colon (`:`) and are separated by commas (`,`).

Multiple filters can be chained together, effectively piping the output of one filter into the input of another. See the [filter reference](filter_reference.md) for details of all built in filters.

```liquid2
{{ user_name | upcase }}
{{ 42 | plus: 7 | modulo: 3 }}
```

## assign

```
{% assign <identifier> = <expression> %}
```

The `assign` tag is used to define and initialize new variables or reassign existing variables.

```liquid2
{% assign foo = "bar" %}
foo is equal to {{ foo }}.

{% assign foo = 42 %}
foo is now equal to {{ foo }}.
```

The _expression_ on the right-hand side of the assignment operator (`=`) follows the syntax described in [Output](#output) above. It can be any [primitive expression](#primitive-expressions) and it can include [filters](#filters).

## capture

```
{% capture <identifier> %} <liquid markup> {% endcapture %}
```

The `capture` tag evaluates the contents of its block and saves the resulting string as a new variable, or reassigns an existing variable, without immediately rendering it.

```liquid2
{% capture welcome_message %}
  Hello, {{ customer.name }}! Welcome to our store.
{% endcapture %}

{{ welcome_message }}
```

In some cases, it can be easier to use a template string.

```liquid2
{% assign welcome_message = "Hello, ${ customer.name }! Welcome to our store." %}
```

## case

```
{% case <expression> %}
  [ {% when <expression> %} <liquid markup> ] ...
  [ {% else %} <liquid markup> ]
{% endcase %}
```

The `case` tag evaluates an expression, matching the result against one or more `when` clauses. In the event of a match, the `when` block is rendered. The `else` clause is rendered if no `when` clauses match the `case` expression.

```liquid2
{% assign day = "Monday" %}

{% case day %}
  {% when "Monday" %}
    Start of the work week!
  {% when "Friday" %}
    It's almost the weekend!
  {% when "Saturday" or "Sunday" %}
    Enjoy your weekend!
  {% else %}
    Just another weekday.
{% endcase %}
```

## cycle

```
{% cycle [ <string or identifier>: ] <expression> [, <expression> ... ] %}
```

Render the next item in an iterator, initializing it and rendering the first value if it does not yet exist. When the items are exhausted, the iterator starts again from the beginning.

```liquid2
{% cycle 'odd', 'even' %}
{% cycle 'odd', 'even' %}
{% cycle 'odd', 'even' %}
```

You can give `cycle` a name to further distinguish multiple iterators with the same items.

```liquid2
{% cycle 'odd', 'even' %}
{% cycle 'odd', 'even' %}
{% cycle inner: 'odd', 'even' %}
```

## decrement

```
{% decrement <identifier> %}
```

The `decrement` tag renders the next value in a named counter, reducing the count by one each time. If a counter with the given name does not already exist, it is created automatically and initialized to zero, before subtracting 1 and outputting `-1`.

```liquid2
{% decrement some %}
{% decrement thing %}
{% decrement thing %}
```

## echo

```
{% echo <expression> %}
```

The `echo` tag is equivalent to output statements, an expression surrounded by `{{` and `}}`, just in tag form. It is mostly used inside [`{% liquid %}`](#liquid) tags where plain output statements are not allowed.

```liquid2
Hello, {% echo you %}!
Hello, {{ you }}!

{% liquid
  for product in collection.products
    echo product.title | capitalize
  endfor
%}
```

Just like output statements and the [`assign`](#assign) tag, the expression can be any [primitive expression](#primitive-expressions) and it can include [filters](#filters).

```liquid2
{% echo "bar" | upcase if x else "baz" | capitalize %}

{% liquid
  for product in collection.products
    echo product.title | capitalize
  endfor
%}
```

## for

```
{% for <identifier> in <expression>
    [ limit: <expression> ] [ offset: <expression> ] [ reversed ] %}
  <liquid markup>
  [ {% else %} <liquid markup> ]
{% endfor %}
```

The `for` tag renders its block once for each item in an iterable object, like an array/list or mapping/dict/hash. If the iterable is empty and an `else` block given, it will be rendered instead.

```liquid2
{% for product in collection %}
    - {{ product.title }}
{% else %}
    No products available
{% endfor %}
```

Range expression are often used with the `for` tag to loop over increasing integers.

```liquid2
{% for i in (1..4) %}
    {{ i }}
{% endfor %}
```

### limit

If a `limit` argument is given, the loop will stop after the specified number of iterations.

```liquid2
{% for product in collection.products limit: 2 %}
    - {{ product.title }}
{% endfor %}
```

### offset

If an `offset` argument is given, it should be an integer specifying how many items to skip before starting the loop.

```liquid2
{% for product in collection.products limit: 2 %}
    - {{ product.title }}
{% endfor %}
```

`offset` can also be given the special value `"continue"`, in which case the loop will start from where a previous loop with the same iterable left off.

```liquid2
{% for product in collection.products limit: 2 %}
    - {{ product.title }}
{% endfor %}

{% for product in collection.products offset: continue %}
    - {{ product.title }}!
{% endfor %}
```

### reversed

If the reversed flag is given, the target iterable will be iterated in reverse order.

```liquid2
{% for product in collection.products reversed %}
    - {{ product.title }}
{% endfor %}
```

### break

You can exit a loop early using the `break` tag.

```liquid2
{% for product in collection.products %}
    {% if product.title == "Shirt" %}
        {% break %}
    {% endif %}
    - {{ product.title }}
{% endfor %}
```

### continue

You can skip all or part of a loop iteration with the `continue` tag.

```liquid2
{% for product in collection.products %}
    {% if product.title == "Shirt" %}
        {% continue %}
    {% endif %}
    - {{ product.title }}
{% endfor %}
```

### forloop

A `forloop` object is available inside every `for` tag block.

| Property     | Description                                                          | Type    |
| ------------ | -------------------------------------------------------------------- | ------- |
| `name`       | The loop variable name and target identifier, separated by a hyphen. | string  |
| `length`     | The length of the sequence being iterated.                           | integer |
| `index`      | The 1-base index of the current iteration.                           | integer |
| `index0`     | The 0-base index of the current iteration.                           | integer |
| `rindex`     | The 1-base index of the current iteration counting from the end.     | integer |
| `rindex0`    | The 0-base index of the current iteration counting from the end.     | integer |
| `first`      | `true` if the current iteration is the first, `false` otherwise.     | bool    |
| `last`       | `true` is the current iteration is the last, `false` otherwise.      | bool    |
| `parentloop` | the `forloop` object of an enclosing `for` loop.                     | forloop |

```liquid2
{% for product in collection.products %}
    {% if forloop.first %}
      <b>{{ product.title }}</b> - {{ forloop.index0 }}
    {% else %}
      {{ product.title }} - {{ forloop.index0 }}
    {% endif %}
{% endfor %}
```

## if

```
{% if <expression> %}
  <liquid markup>
  [ {% elsif <expression> %} <liquid markup> [ {% elsif <expression> %} ... ]]
  [ {% else %} <liquid markup> ... ]
{% endif %}
```

The `if` tag conditionally renders its block if its expression evaluates to be truthy. Any number of `elsif` blocks can be given to add alternative conditions, and an `else` block is used as a default if no preceding conditions were truthy.

```liquid2
{% if product.title == "OK Hat" %}
  This hat is OK.
{% elsif product.title == "Rubbish Tie" %}
  This tie is rubbish.
{% else %}
  Not sure what this is.
{% endif %}
```

### Conditional expressions

Any primitive expression can be tested for truthiness, like `{% if some_variable %}`, or you can use a combination of the following operators. Only `false`, `nil`/`null` and the special _undefined_ object are falsy in Liquid.

| Operator | Description              | Example                             |
| -------- | ------------------------ | ----------------------------------- |
| `==`     | Equals                   | `product.title == "Nice Shoes"`     |
| `!=`     | Not equals               | `user.name != "anonymous"`          |
| `>`      | Greater than             | `product.was_price > product.price` |
| `<`      | Less than                | `collection.products.size < 10`     |
| `>=`     | Greater than or equal to | `user.age >= 18`                    |
| `<=`     | Less than or equal to    | `basket.size <= 0`                  |
| `and`    | Logical and              | `x and y`                           |
| `or`     | Logical or               | `x or y`                            |

### Operator precedence

In Liquid, `and` and `or` operators are right associative. Where `true and false and false or true` is equivalent to `(true and (false and (false or true)))`, evaluating to `false`. Python, on the other hand, would parse the same expression as `(((true and false) and false) or true)`, evaluating to `true`.

## include

```liquid2
{% include <template name>
    [ ( with | for ) <expression> [ as <identifier> ]]
    [[,] <identifier>: <expression> [, [<identifier>: <expression> ... ]]]
%}
```

The `include` tag loads and renders a named template, inserting the resulting text in its place. The name of the template to include can be a string literal or a variable resolving to a string. When rendered, the included template will share the same scope as the current template.

```liquid2
{% include "snippets/header.html" %}
```

### with

Using the optional `with` syntax, we can bind a value to a variable that will be in scope for the included template. By default, that variable will be the name of the included template. Alternatively we can specify the variable to use with the `as` keyword followed by an identifier.

Here, the template named `greeting` will have access to a variable called `greeting` with the value `"Hello"`.

```liquid2
{% assign greetings = "Hello,Goodbye" | split: "," %}
{% include "greeting" with greetings.first %}
```

### for

If an array-like object it given following the `for` keyword, the named template will be rendered once for each item in the sequence and, like `with` above, the item value will be bound to a variable named after the included template.

In this example the template named `greeting` will be rendered once with the variable `greeting` set to `"Hello"` and once with the variable `greeting` set to `"Goodbye"`.

```liquid2
{% assign greetings = "Hello, Goodbye" | split: ", " %}
{% include "greeting" for greetings as greeting %}
```

### Keyword arguments

Additional keyword arguments given to the `include` tag will be added to the included template's scope, then go out of scope after the included template has been rendered.

```liquid2
{% include "partial_template" greeting: "Hello", num: 3, skip: 2 %}
```

## increment

```
{% increment <identifier> %}
```

The `increment` tag renders the next value in a named counter, increasing the count by one each time. If a counter with the given name does not already exist, it is created automatically and initialized to zero, which is output **before** adding `1`.

```liquid2
{% increment some %}
{% increment thing %}
{% increment thing %}
```

## liquid

```
{% liquid
  <tag name> [<expression>]
  [ <tag name> [<expression>]]
  ...
%}
```

The `liquid` tag encloses _line statements_, where each line starts with a tag name and is followed by the tag's expression. Expressions inside `liquid` tags **must** fit on one line as we use `\n` as a delimiter indicating the end of the expression.

Note that output statement syntax (`{{ <expression> }}`) is not allowed inside `liquid` tags, so you must use the [`echo`](#echo) tag instead.

```liquid2
{% liquid
  assign username = "Brian"

  if username
    echo "Hello, " | append: username
  else
    echo "Hello, user"
  endif

  for i in (1..3)
    echo i
  endfor
%}
```

Also, inside `liquid` tags, any line starting with a hash will be considered a comment.

```liquid2
{% liquid
  # This is a comment
  echo "Hello"
%}
```

## raw

```
{% raw %} <text> {% endraw %}
```

Any text between `{% raw %}` and `{% endraw %}` will not be interpreted as Liquid markup, but output as plain text instead.

```liquid2
{% raw %}
  This will be rendered {{verbatim}}, with the curly brackets.
{% endraw %}
```

## render

```liquid2
{% render <string>
    [ ( with | for ) <expression> [ as <identifier> ]]
    [[,] <identifier>: <expression> [, [<identifier>: <expression> ... ]]]
%}
```

The `render` tag loads and renders a named template, inserting the resulting text in its place. The name of the template to include **must** be a string literal. When rendered, the included template will have its onw scope, without variables define in the calling template.

```liquid2
{% render "snippets/header.html" %}
```

### with

Using the optional `with` syntax, we can bind a value to a variable that will be in scope for the rendered template. By default, that variable will be the name of the rendered template. Alternatively we can specify the variable to use with the `as` keyword followed by an identifier.

Here, the template named `greeting` will have access to a variable called `greeting` with the value `"Hello"`.

```liquid2
{% assign greetings = "Hello,Goodbye" | split: "," %}
{% render "greeting" with greetings.first %}
```

### for

If an array-like object it given following the `for` keyword, the named template will be rendered once for each item in the sequence and, like `with` above, the item value will be bound to a variable named after the rendered template.

In this example the template named `greeting` will be rendered once with the variable `greeting` set to `"Hello"` and once with the variable `greeting` set to `"Goodbye"`.

```liquid2
{% assign greetings = "Hello, Goodbye" | split: ", " %}
{% render "greeting" for greetings as greeting %}
```

### Keyword arguments

Additional keyword arguments given to the `render` tag will be added to the rendered template's scope, then go out of scope after the it has been rendered.

```liquid2
{% render "partial_template" greeting: "Hello", num: 3, skip: 2 %}
```

## tablerow

<!-- md:version 0.1.0 -->
<!-- md:shopify -->

```plain
{% tablerow <identifier> in <expression>
    [ cols: <expression> ] [ limit: <expression> ] [ offset: <expression> ] %}
  <liquid markup>
{% endtablerow %}
```

The `tablerow` tag renders HTML `<tr>` and `<td>` elements for each item in an iterable. Text inside `<td>` elements will be the result of rendering the tag's block.

```json title="data"
{
  "collection": {
    "products": [
      { "title": "Cool Shirt" },
      { "title": "Alien Poster" },
      { "title": "Batman Poster" },
      { "title": "Bullseye Shirt" },
      { "title": "Another Classic Vinyl" },
      { "title": "Awesome Jeans" }
    ]
  }
}
```

```liquid2 title="template"
<table>
{% tablerow product in collection.products %}
  {{ product.title }}
{% endtablerow %}
</table>
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Cool Shirt</td>
    <td class="col2">Alien Poster</td>
    <td class="col3">Batman Poster</td>
    <td class="col4">Bullseye Shirt</td>
    <td class="col5">Another Classic Vinyl</td>
    <td class="col6">Awesome Jeans</td>
  </tr>
</table>
```

### cols

By default, `tablerow` will output one row with one column for each item in the sequence. Use the `cols` parameter to set the number of columns.

```liquid2 title="template"
{% tablerow product in collection.products cols:2 %}
  {{ product.title }}
{% endtablerow %}
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Cool Shirt</td>
    <td class="col2">Alien Poster</td>
  </tr>
  <tr class="row2">
    <td class="col1">Batman Poster</td>
    <td class="col2">Bullseye Shirt</td>
  </tr>
  <tr class="row3">
    <td class="col1">Another Classic Vinyl</td>
    <td class="col2">Awesome Jeans</td>
  </tr>
</table>
```

### limit

If `limit` is specified, the `tablerow` loop will stop after the given number of iterations.

```liquid2 title="template"
<table>
{% tablerow product in collection.products limit:2 %}
  {{ product.title }}
{% endtablerow %}
</table>
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Cool Shirt</td>
    <td class="col2">Alien Poster</td>
  </tr>
</table>
```

### offset

If `offset` is specified, the `tablerow` loop will start at the given index in the sequence.

```liquid2 title="template"
<table>
{% tablerow product in collection.products offset:4 %}
  {{ product.title }}
{% endtablerow %}
</table>
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Another Classic Vinyl</td>
    <td class="col2">Awesome Jeans</td>
  </tr>
</table>
```

### tablerowloop

A `tablerowloop` object is available inside every `tablerow` block.

| Property    | Description                                                         | Type    |
| ----------- | ------------------------------------------------------------------- | ------- |
| `length`    | The length of the sequence being iterated                           | integer |
| `index`     | The 1-base index of the current iteration                           | integer |
| `index0`    | The 0-base index of the current iteration                           | integer |
| `rindex`    | The 1-base index of the current iteration counting from the end     | integer |
| `rindex0`   | The 0-base index of the current iteration counting from the end     | integer |
| `first`     | `true` if the current iteration is the first, `false` otherwise     | bool    |
| `last`      | `true` is the current iteration is the last, `false` otherwise      | bool    |
| `col`       | The 1-based column number                                           | integer |
| `col0`      | The 0-based column number                                           | integer |
| `col_first` | `true` if the current column is the first column, `false` otherwise | integer |
| `col_last`  | `true` if the current column is the last column, `false` otherwise  | integer |
| `row`       | The current row number of the table                                 | integer |

```liquid2 title="template"
{% tablerow product in collection.products cols:2 %}
  {{ product.title }} - {{ tablerowloop.col0 }}
{% endtablerow %}
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Cool Shirt - 0</td>
    <td class="col2">Alien Poster - 1</td>
  </tr>
  <tr class="row2">
    <td class="col1">Batman Poster - 0</td>
    <td class="col2">Bullseye Shirt< - 1/td></td>
  </tr>
  <tr class="row3">
    <td class="col1">Another Classic Vinyl - 0</td>
    <td class="col2">Awesome Jeans - 1</td>
  </tr>
</table>
```

## unless

```
{% unless <expression> %}
  <liquid markup>
  [ {% elsif <expression> %} <liquid markup> [ {% elsif <expression> %} ... ]]
  [ {% else %} <liquid markup> ... ]
{% endif %}
```

The `unless` tag conditionally renders its block if its expression evaluates to be falsy. Any number of elsif blocks can be given to add alternative conditions, and an else block is used as a default if none of preceding conditions were met.

```liquid2
{% unless product.title == "OK Hat" %}
  This hat is OK.
{% elsif product.title == "Rubbish Tie" %}
  This tie is rubbish.
{% else %}
  Not sure what this is.
{% endif %}
```

Otherwise `unless` behaves the same as [`if`](#if). See [Conditional expressions](#conditional-expressions).


=== File: docs/variables_and_drops.md ===
Liquid _primitive types_ map to Python types according to the following table. You can, for example, compare a Liquid string to a Python string directly with `{% if var == "thing" %}`, where `var` is a [global](render_context.md) variable containing a Python string.

Note that Liquid has _weak typing_. Anywhere a particular type is expected, Liquid will implicitly try to convert a value to that type if needed.

| Primitive type | Python type | Example Liquid literal |
| -------------- | ----------- | ---------------------- |
| BooleanLiteral | bool        | `true` or `false`      |
| NullLiteral    | None        | `null` or `nil`        |
| IntegerLiteral | int         | `123`                  |
| FloatLiteral   | float       | `1.23`                 |
| StringLiteral  | str         | `"Hello"` or `'Hello'` |
| RangeLiteral   |             | `(1..5)` or `(x..y)`   |

## Sequences and mappings

Anywhere an array-like value is expected, like the left-hand side of the [`join` filter](filter_reference.md#join), Liquid will accept any Python [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence), not just a list.

In the case of a [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping), like a dict, a `{% for %}` loop will iterator over mapping items, whereas a sequence filter will add the mapping to a single element sequence and iterate over that.

```python
from collections.abc import Sequence
from liquid import render


class MySequence(Sequence[int]):
    def __init__(self, items: list[int]):
        self.items = items

    def __getitem__(self, key: int) -> int:
        return self.items[key] * 2

    def __len__(self) -> int:
        return len(self.items)


data = {
    "sequences": [
        MySequence([1, 2, 3]),
        ["a", "b", "c"],
        (True, False),
        {"x": 4, "y": 5, "z": 6},
    ]
}

source = """\
{% for sequence in sequences -%}
    {% for item in sequence %}
        - {{ item -}}
    {% endfor %}
{% endfor %}
"""

print(render(source, **data))

```

```plain title="output"
        - 2
        - 4
        - 6

        - a
        - b
        - c

        - true
        - false

        - ('x', 4)
        - ('y', 5)
        - ('z', 6)
```

## Paths to variables

When referenced in a template, a variable is best viewed as a _path_ to a value, where each path has one or more _segments_. Segments can be property names separated by dots (`foo.bar`), array indexes using bracket notation (`store.products[1]`) or bracketed property names for situations where the property name is held in a variable or contains reserved characters (`product.variant[var]` or `products["something with spaces"]`)

Python Liquid uses [`__getitem__`](https://docs.python.org/3/reference/datamodel.html#object.__getitem__) internally for resolving property names and accessing items in a sequence. So, if your data is some combination of dictionaries and lists, for example, templates can reference objects as follows.

```json title="data"
{
  "products": [
    {
      "title": "Some Shoes",
      "available": 5,
      "colors": ["blue", "red"]
    },
    {
      "title": "A Hat",
      "available": 2,
      "colors": ["grey", "brown"]
    }
  ]
}
```

```liquid title="template"
{{ products[0].title }}
{{ products[-2]['available'] }}
{{ products.last.title }}
{{ products.first.colors | join: ', ' }}
```

```plain title="output"
Some Shoes
5
A Hat
blue, red
```

Attempting to access properties from a Python class or class instance **will not work**.

```python
from liquid import Template

class Product:
    def __init__(self, title, colors):
        self.title = title
        self.colors = colors

products = [
    Product(title="Some Shoes", colors=["blue", "red"]),
    Product(title="A Hat", colors=["grey", "brown"]),
]

Template("{{ products.first.title }}!").render(products=products)
```

```plain title="output"
!
```

## Drops

A _drop_ (as in "drop of liquid") is an instance of a Python class that implements the [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence) or [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) interface, or other [magic methods](#other-magic-methods).

We use the Mapping interface to force ourselves to be explicit about which properties are exposed to template authors.

```python
from collections import abc
from typing import Any

from liquid import Environment
from liquid import StrictUndefined
from liquid import render


class User(abc.Mapping[str, Any]):
    def __init__(
        self,
        first_name: str,
        last_name: str,
        perms: list[str],
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.perms = perms or []

        self._keys = [
            "first_name",
            "last_name",
            "is_admin",
            "name",
        ]

    def __getitem__(self, k):
        if k in self._keys:
            return getattr(self, k)
        raise KeyError(k)

    def __iter__(self):
        return iter(self._keys)

    def __len__(self):
        return len(self._keys)

    def __str__(self):
        return f"User(first_name='{self.first_name}', last_name='{self.last_name}')"

    @property
    def is_admin(self):
        return "admin" in self.perms

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


user = User("John", "Smith", ["admin"])

print(render("{{ user.first_name }}", user=user))  # John
print(render("{{ user.name }}", user=user))  # John Smith
print(render("{{ user.is_admin }}", user=user))  # true


strict_env = Environment(undefined=StrictUndefined)
print(strict_env.from_string("{{ user.perms[0] }}").render(user=user))
# liquid.exceptions.UndefinedError: user.perms is undefined
#   -> '{{ user.perms[0] }}' 1:3
#   |
# 1 | {{ user.perms[0] }}
#   |    ^^^^ user.perms is undefined

```

### Drop wrapper

For convenience, you could implement a drop wrapper for data access objects, while still being explicit about which properties to expose.

```python
class Drop(abc.Mapping):
    def __init__(obj, keys):
        self.obj = obj
        self.keys = keys

    def __getitem__(self, k):
        # Delegate attribute access to self.obj only if `k` is in `self.keys`.
        if k in self.keys:
            return getattr(obj, k)
        raise KeyError(k)

    def __iter__(self):
        return iter(self.keys)

    def __len__(self):
        return len(self.keys)
```

### `__liquid__`

If a drop implements the special `__liquid__()` method, Liquid will use the result of calling `__liquid__()` when resolving a [variable path or segment](#paths-to-variables). This is useful for situations where you need your Python object to act as an array index, or to be compared to a primitive data type, for example.

```python
from liquid import parse

class IntDrop:
    def __init__(self, val: int):
        self.val = val

    def __int__(self) -> int:
        return self.val

    def __str__(self) -> str:
        return "one"

    def __liquid__(self) -> int:
        return self.val


template = parse(
    "{% if my_drop < 10 %}"
    "{{ my_drop }} "
    "{% endif %}"
    "{{ some_array[my_drop] }}"
)

context_data = {
    "my_drop": IntDrop(1),
    "some_array": ["a", "b", "c"],
}

print(template.render(**context_data))  # one b
```

### `__html__`

When [HTML auto-escaping](environment.md#html-auto-escape) is enabled, an object can be output as an HTML-safe string by implementing the special `__html__()` method.

```python
from liquid import Environment


class ListDrop:
    def __init__(self, somelist):
        self.items = somelist

    def __str__(self):
        return f"ListDrop({self.items})"

    def __html__(self):
        lis = "\n".join(f"  <li>{item}</li>" for item in self.items)
        return f"<ul>\n{lis}\n</ul>"


env = Environment(auto_escape=True)
template = env.from_string(r"{{ products }}")
print(template.render(products=ListDrop(["Shoe", "Hat", "Ball"])))
```

```plain title="output"
<ul>
  <li>Shoe</li>
  <li>Hat</li>
  <li>Ball</li>
</ul>
```

### `__getitem_async__`

If an instance of a drop that implements `__getitem_async__()` appears in a [`render_async()`](api/template.md#liquid.BoundTemplate.render_async) context, `__getitem_async__()` will be awaited instead of calling `__getitem__()`.

```python
class AsyncCollection(abc.Mapping):
    def __init__(self, val):
        self.keys = ["products"]
        self.cached_products = []

    def __len__(self):
        return 1

    def __iter__(self):
        return iter(self["products"])

    async def __aiter__(self):
        # Note that Liquid's built-in `for` loop does not yet support async iteration.
        return iter(self.__getitem_async__("products"))

    def __getitem__(self, k):
        if not self.cached_products:
            # Blocking IO here
            self.cached_products = get_stuff_from_database()
        return self.cache_products

    async def __getitem_async__(self, k):
        if not self.cached_products:
            # Do async IO here.
            self.cached_products = await get_stuff_from_database_async()
        return self.cache_products
```

### Other magic methods

Other Python [magic methods](https://docs.python.org/3/reference/datamodel.html) will work with Liquid filters and special properties too.

```python
from liquid import Environment

env = Environment()

class Foo:
    def __int__(self):
        return 7

    def __str__(self):
        return "Bar"

    def __len__(self):
        return 5


template = env.from_string(
    """\
{{ foo }}
{{ foo | plus: 2 }}
{{ foo.size }}
"""
)

print(template.render(foo=Foo()))
```

```plain title="output"
Bar
9
5
```

## Undefined variables

At render time, if a variable can not be resolved, and instance of [`Undefined`](api/undefined.md) is used instead. We can customize template rendering behavior by implementing some of [Python's "magic" methods](https://docs.python.org/3/reference/datamodel.html#basic-customization) on a subclass of `Undefined`.

### Default undefined

All operations on the default `Undefined` type are silently ignored and, when rendered, it produces an empty string. For example, you can access properties and iterate an undefined variable without error.

```liquid
Hello {{ nosuchthing }}
{% for thing in nosuchthing %}
    {{ thing }}
{% endfor %}
```

```plain title="output"
Hello



```

### Strict undefined

When [`StrictUndefined`](api/undefined.md#liquid.StrictUndefined) is passed as the `undefined` argument to an [`Environment`](api/environment.md), any operation on an undefined variable will raise an `UndefinedError`.

```python
from liquid import Environment, StrictUndefined

env = Environment(undefined=StrictUndefined)
template = env.from_string("Hello {{ nosuchthing }}")
template.render()
# liquid.exceptions.UndefinedError: 'nosuchthing' is undefined
#   -> 'Hello {{ nosuchthing }}' 1:9
#   |
# 1 | Hello {{ nosuchthing }}
#   |          ^^^^^^^^^^^ 'nosuchthing' is undefined
```

### Falsy strict undefined

[`FalsyStrictUndefined`](api/undefined.md#liquid.FalsyStrictUndefined) is the same as [`StrictUndefined`](#strict-undefined), but can be tested for truthiness and equality without raising an exception.

```python
from liquid import Environment
from liquid import FalsyStrictUndefined

env = Environment(undefined=FalsyStrictUndefined)
template = env.from_string("{% if nosuchthing %}foo{% else %}bar{% endif %}")
print(template.render())  # bar
```


#include <stdio.h>


#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <std_msgs/msg/float32.h>
#include <std_msgs/msg/int32.h>
#include <rmw_microros/rmw_microros.h>
#include <std_msgs/msg/color_rgba.h>
#include "pico/stdlib.h"
#include "pico_uart_transports.h"
#include "hardware/adc.h"
#include <PicoLed.hpp>

const uint LED_PIN = 12;
const uint ADC_PIN = 0;
const uint LED_LENGTH = 24;
const uint FAN_PIN = 27;

rcl_publisher_t publisher;
std_msgs__msg__Float32 msg;

PicoLed::PicoLedController *ledStripPtr;

rcl_subscription_t subscriber;
std_msgs__msg__ColorRGBA sub_msg;

rcl_subscription_t subscriberFAN;
std_msgs__msg__Int32 FANsub_msg;


void timer_callback(rcl_timer_t *timer, int64_t last_call_time)
{
    rcl_ret_t ret = rcl_publish(&publisher, &msg, NULL);
    msg.data = (adc_read()/4095.0)*16.5;
}

void subscription_callback(const void * msgin)
{
    // Cast received message to used type
    const std_msgs__msg__ColorRGBA * msg = (const std_msgs__msg__ColorRGBA *)msgin;
    ledStripPtr->fill( PicoLed::RGB(msg->r*255, msg->g*255, msg->b*255) );
    ledStripPtr->show();
}

void subscription_callback_FAN(const void * msgin)
{
    // write int value to fan > 0 will switch fan on - pwm control to come. 
    gpio_put(FAN_PIN, FANsub_msg.data);
}

int main()
{
    adc_init();
    adc_select_input(0);

    rmw_uros_set_custom_transport(
		true,
		NULL,
		pico_serial_transport_open,
		pico_serial_transport_close,
		pico_serial_transport_write,
		pico_serial_transport_read
	);
        
    stdio_init_all();
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);


    gpio_init(FAN_PIN);
    gpio_set_dir(FAN_PIN, GPIO_OUT);

    
    
    
    auto ledStrip = PicoLed::addLeds<PicoLed::WS2812B>(pio0, 0, LED_PIN, LED_LENGTH, PicoLed::FORMAT_GRB);
    ledStripPtr = &ledStrip;
    ledStrip.setBrightness(255);

    rcl_timer_t timer;
    rcl_node_t node;
    rcl_allocator_t allocator;
    rclc_support_t support;
    rclc_executor_t executor;

    allocator = rcl_get_default_allocator();

    // Wait for agent successful ping for 2 minutes.
    const int timeout_ms = 1000; 
    const uint8_t attempts = 120;

    rcl_ret_t ret = rmw_uros_ping_agent(timeout_ms, attempts);

    if (ret != RCL_RET_OK)
    {
        // Unreachable agent, exiting program.
        return ret;
    }

    rclc_support_init(&support, 0, NULL, &allocator);

    rclc_node_init_default(&node, "hardware_node", "", &support);
    rclc_publisher_init_default(
        &publisher,
        &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Float32),
        "chassis/vbus");

    rcl_ret_t rc = rclc_subscription_init_default(
        &subscriber, &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, ColorRGBA),
        "chassis/NeoLED");

    rcl_ret_t rca = rclc_subscription_init_default(
        &subscriberFAN, &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
        "chassis/Fans");

    rclc_timer_init_default(
        &timer,
        &support,
        RCL_MS_TO_NS(1000),
        timer_callback);

    rclc_executor_init(&executor, &support.context, 3, &allocator);
    rclc_executor_add_timer(&executor, &timer);
        // Add subscription to the executor

    rc = rclc_executor_add_subscription(
        &executor, &subscriber, &sub_msg,
        &subscription_callback, ON_NEW_DATA);

    rca = rclc_executor_add_subscription(
        &executor, &subscriberFAN, &FANsub_msg,
        &subscription_callback_FAN, ON_NEW_DATA);


    msg.data = 0;
    while (true)
    {
        rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100));
    }
    return 0;
}



#ifndef __SAFE_INT_H__
#define __SAFE_INT_H__


#include <exception>
#include <cstddef>

#include <iostream>

class SafeIntException : public std::exception
{


};

typedef signed long SL;


namespace mh_int32
{



    class SafeInt32
    {


        static const NativeInt32 nbits = 32;
        //static const int nbits = 25;
        static const NativeInt64 int32_max = (1l<<(nbits-1)) - 1;
        static const NativeInt64 int32_min = -(1l<<(nbits-1)) - 1;


        int _value;
        bool is_valid;

    public:


        static SafeInt32 from_long(NativeInt64 value)
        {
            assert( value < int32_max && value > int32_min);

            NativeInt32 v = value;
            assert( v == value);

            return SafeInt32(v);
        }

        NativeInt32 get_value32() const
        {
            return _value;
        }

        NativeInt64 get_value64() const
        {
            return _value;
        }


        static
        void check_value(NativeInt64 value)
        {

            

            if(value < 0) value = -value;

            NativeInt64 masked = (value & 0xFFFFFFFF);
            if( value != masked )
            {

                std::cout << "\n ** Truncation Error! ** \n";
                assert(0);

            }
        };


        explicit SafeInt32(NativeInt32 value)
            : _value(value), is_valid(true)
        {
            check_value(value);
            if( (SL)_value > (SL)int32_max || (SL)_value < (SL) int32_min )
            {
                throw SafeIntException();
            }
        }


        explicit SafeInt32()
            : _value(0), is_valid(false)
        {

        }





        bool is_positive() const
        {
            return (_value >= 0);
        }

        friend SafeInt32 operator+(SafeInt32 a, SafeInt32 b);
        friend SafeInt32 operator-(SafeInt32 a, SafeInt32 b);
        friend SafeInt32 operator*(SafeInt32 a, SafeInt32 b);
        friend SafeInt32 operator/(SafeInt32 a, SafeInt32 b);
        friend SafeInt32 operator<<(const SafeInt32& a, const SafeInt32& b);
        friend SafeInt32 operator>>(const SafeInt32& a, const SafeInt32& b);
        friend SafeInt32 operator+(SafeInt32 a, NativeInt32 b);
        friend SafeInt32 operator-(SafeInt32 a, NativeInt32 b);
        friend SafeInt32 operator*(SafeInt32 a, NativeInt32 b);

        bool operator==(const SafeInt32& rhs) const
        {
            assert(this->is_valid && rhs.is_valid);
            return _value == rhs._value;
        }

        bool operator<(const SafeInt32& rhs) const
        {
            assert(this->is_valid && rhs.is_valid);
            return _value < rhs._value;
        }

        // Comparisons against ints:
        bool operator==(NativeInt32 rhs) const
        {
            assert(this->is_valid);
            return _value == rhs;
        }
        bool operator!=(NativeInt32 rhs) const
        {
            assert(this->is_valid);
            return _value != rhs;
        }
        bool operator>(NativeInt32 b) const
        {
            assert(this->is_valid);
            return _value > b;
        }
        bool operator<(NativeInt32 b) const
        {
            assert(this->is_valid);
            return _value < b;
        }
        bool operator>=(NativeInt32 b) const
        {
            assert(this->is_valid);
            return _value >= b;
        }
        SafeInt32 operator-() const
        {
            assert(this->is_valid);
            return SafeInt32(-_value);
        }


        SafeInt32& operator+=(const SafeInt32& rhs)
        {
            assert(this->is_valid && rhs.is_valid);
            SafeInt32 s = *this + rhs;
            this->_value = s._value;
            return *this;
        }

        SafeInt32 operator++(int)
        {
            SafeInt32 temp(this->_value);
            SafeInt32 new_val = *this + SafeInt32(1);
            this->_value = new_val._value;
            return temp;
        }


//#SafeInt operator+=(const SafeInt32& rhs)
//        {
//            
//            assert(this->is_valid && rhs.is_valid);
//            SafeInt32 s = *this + rhs;
//            this->_value = s._value;
//
//            return *this;
//        }

    };


    SafeInt32 operator+(SafeInt32 a, SafeInt32 b)
    {
        assert(a.is_valid && b.is_valid);

        if(a.is_positive() )
        {
            if( b.is_positive() )
            {
                // Check for overflow:
                if( (SL)SafeInt32::int32_max - (SL) a._value  < (SL) b._value )
                {
                    std::cout << "\n\nEh Oh! (SafeInt32 operator+(SafeInt32 a, SafeInt32 b)) Overflow detected! ( " << (SL) a._value << " + " << (SL) b._value << " )\n\n";
                    throw SafeIntException();
                }

            }
            else
            {
                // (+) + (-) This should be OK, because we must still be in range
            }
        }
        else
        {
            if( b.is_positive() )
            {
                // (-) + (+) This should be OK, because we must still be in range

            }
            else
            {
                // (-) + (-)
                // Check for underflow:
                //std::cout << "int32_min: " << int32_min << "\n" << std::flush;
                if( (SL)SafeInt32::int32_min + ((SL) b._value ) * -1  > (SL)a._value )
                {
                    throw SafeIntException();
                }

            }
        }
        return SafeInt32( a._value + b._value );
    }

    SafeInt32 operator-(SafeInt32 a, SafeInt32 b)
    {
        assert(a.is_valid && b.is_valid);
        // TODO: Check for overflow/underflow here:
        return SafeInt32( a._value - b._value);
    }

    SafeInt32 operator*(SafeInt32 a, SafeInt32 b)
    {
        assert(a.is_valid && b.is_valid);
        // TODO: Check for overflow/underflow here:
        SafeInt32 res = SafeInt32( a._value * b._value);

        // Simple sanity check:
        SafeInt32::check_value(a._value);
        SafeInt32::check_value(b._value);
        SafeInt32::check_value(res._value);

        return res;
    }

    SafeInt32 operator/(SafeInt32 a, SafeInt32 b)
    {
        assert(a.is_valid && b.is_valid);
        // TODO: Check for overflow/underflow here:
        SafeInt32 res = SafeInt32( a._value / b._value);

        // Simple sanity check:
        SafeInt32::check_value(a._value);
        SafeInt32::check_value(b._value);
        SafeInt32::check_value(res._value);

        return res;

    }

    SafeInt32 operator<<(const SafeInt32& a, const SafeInt32& b)
    {
        assert(a.is_valid && b.is_valid);
        // TODO: Check for overflow/underflow here:
        assert(b._value >= 0 );
        SafeInt32 res = SafeInt32( a._value << b._value);

        // Simple sanity check:
        SafeInt32::check_value(a._value);
        SafeInt32::check_value(b._value);
        SafeInt32::check_value(res._value);

        return res;
    }

    SafeInt32 operator>>(const SafeInt32& a, const SafeInt32& b)
    {
        assert(a.is_valid && b.is_valid);
        // TODO: Check for overflow/underflow here:
        assert(b._value >= 0 );
        SafeInt32 res = SafeInt32( a._value >> b._value);
        
        // Simple sanity check:
        SafeInt32::check_value(a._value);
        SafeInt32::check_value(b._value);
        SafeInt32::check_value(res._value);

        return res;
    }


    SafeInt32 operator+(SafeInt32 a, NativeInt32 b)
    {
        assert(a.is_valid);
        return a + SafeInt32(b);
    }

    SafeInt32 operator-(SafeInt32 a, NativeInt32 b)
    {
        assert(a.is_valid);
        return a - SafeInt32(b);
    }

    SafeInt32 operator*(SafeInt32 a, NativeInt32 b)
    {
        assert(a.is_valid);
        return a * SafeInt32(b);
    }




}









/*

namespace mh_uint32
{


    const size_t uint32_max = (1l<<32) - 1;
    class SafeUInt32
    {

        unsigned int _value;

    public:
        explicit SafeUInt32(unsigned int value)
            : _value(value)
        {
            if( uint32_max < _value )
            {
                throw SafeIntException();
            }

        }

        friend SafeUInt32 operator+(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator-(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator*(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator/(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator<<(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator>>(SafeUInt32 a, SafeUInt32 b);


        bool operator==(const SafeUInt32& rhs)
        {
            return _value == rhs._value;
        }

    };



    SafeUInt32 operator+(SafeUInt32 a, SafeUInt32 b)
    {
        // Check for overflow:
        if( uint32_max - a._value < b._value )
        {
            throw SafeIntException();
        }
        return SafeUInt32( a._value + b._value );
    }

    SafeUInt32 operator-(SafeUInt32 a, SafeUInt32 b)
    {
        // Check for underflow:
        if( a._value < b._value )
        {
            throw SafeIntException();
        }
        return SafeUInt32( a._value - b._value );
    }

    SafeUInt32 operator*(SafeUInt32 a, SafeUInt32 b)
    {
        // Check for overflow:
        if( uint32_max / b._value < a._value )
        {
            throw SafeIntException();
        }
        return SafeUInt32( a._value * b._value );
    }

    SafeUInt32 operator/(SafeUInt32 a, SafeUInt32 b)
    {
        if( b._value == 0 )
        {
            throw SafeIntException();
        }
        return SafeUInt32( a._value / b._value );
    }

    SafeUInt32 operator<<(SafeUInt32 a, SafeUInt32 b)
    {
        // TODO: Ensure that the top bits 'b' are zero:
        return SafeUInt32( a._value << b._value );
    }

    SafeUInt32 operator>>(SafeUInt32 a, SafeUInt32 b)
    {
        // TODO: Ensure that the top bits 'b' are zero:
        return SafeUInt32( a._value >> b._value );
    }

};


*/


//using namespace mh_uint32;
using namespace mh_int32;






#endif // __SAFE_INT_H__
